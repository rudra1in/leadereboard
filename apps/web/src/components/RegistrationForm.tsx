import { useState, useEffect, useRef } from 'react';

interface Props {
  eventId: number;
  eventTitle: string;
}

interface RegistrationResponse {
  registration_id: string;
  event_id: number;
  full_name: string;
  email: string;
  phone: string;
  status: string;
  message?: string;
}

interface FormErrors {
  [key: string]: string;
}

export default function RegistrationForm({ eventId, eventTitle }: Props) {
  // ============================================================
  // ENVIRONMENT & CONFIGURATION
  // ============================================================
  const API_BASE_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
  const REGISTRATION_ENDPOINT = `${API_BASE_URL}/api/v1/registrations`;
  const SSE_ENDPOINT = `${API_BASE_URL}/api/v1/sse/registrations`;

  // ============================================================
  // STATE MANAGEMENT
  // ============================================================
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
  });

  const [status, setStatus] = useState<
    'idle' | 'submitting' | 'processing' | 'success' | 'error'
  >('idle');

  const [errors, setErrors] = useState<FormErrors>({});
  const [message, setMessage] = useState('');
  const [registrationId, setRegistrationId] = useState<string | null>(null);
  const [registrationData, setRegistrationData] = useState<RegistrationResponse | null>(null);
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // ============================================================
  // VALIDATION FUNCTIONS
  // ============================================================
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Full Name validation
    if (!form.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    } else if (form.full_name.trim().length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters';
    } else if (form.full_name.trim().length > 100) {
      newErrors.full_name = 'Full name must be less than 100 characters';
    }

    // Email validation
    if (!form.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Phone validation (optional but format check if provided)
    if (form.phone) {
      if (!/^\+?[\d\s\-()]{10,}$/.test(form.phone)) {
        newErrors.phone = 'Please enter a valid phone number (at least 10 digits)';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ============================================================
  // FORM SUBMISSION HANDLER
  // ============================================================
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setMessage('');
    setErrors({});

    // Validate form
    if (!validateForm()) {
      setStatus('error');
      setMessage('Please fix the errors above');
      return;
    }

    setStatus('submitting');

    try {
      // Set timeout for request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      // Make registration request
      const response = await fetch(REGISTRATION_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          event_id: eventId,
          full_name: form.full_name.trim(),
          email: form.email.trim().toLowerCase(),
          phone: form.phone.trim() || null,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle response
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const data: RegistrationResponse = await response.json();

      if (!data.registration_id) {
        throw new Error('Invalid server response: missing registration_id');
      }

      // Store registration data and ID
      setRegistrationId(data.registration_id);
      setRegistrationData(data);
      setStatus('processing');
      setMessage('Registration submitted! Waiting for confirmation...');

      // Start listening for SSE updates
      listenForSSEUpdates(data.registration_id);
    } catch (err) {
      handleError(err);
    }
  };

  // ============================================================
  // SSE EVENT LISTENER
  // ============================================================
  const listenForSSEUpdates = (regId: string) => {
    const eventSource = new EventSource(`${SSE_ENDPOINT}/${regId}`);
    eventSourceRef.current = eventSource;

    // Handle registration update
    eventSource.addEventListener('registration_update', (event) => {
  try {
    console.log("Raw SSE data received:", event.data);

    // Parse JSON (safeguard in case backend emits Python dict string representation)
    let parsedData: any;
    try {
      parsedData = JSON.parse(event.data);
    } catch {
      // Fallback: replace unescaped single quotes with double quotes
      const sanitized = event.data.replace(/'/g, '"');
      parsedData = JSON.parse(sanitized);
    }

    setStatus('success');
    setMessage(parsedData.message || 'Registration confirmed!');
    setRegistrationData((prev) => ({
      ...prev!,
      status: parsedData.status || 'confirmed',
    }));

    setShowModal(true);
    eventSource.close();
  } catch (err) {
    console.error('Error parsing SSE data:', err);
    setStatus('error');
    setMessage('Error processing confirmation');
    eventSource.close();
  }
});
    

    // Handle errors
    eventSource.onerror = () => {
      console.error('SSE connection error');
      setStatus('error');
      setMessage('Connection lost. Registration may still be processing.');
      eventSource.close();
    };

    // Handle connection timeout (60 seconds)
    const sseTimeout = setTimeout(() => {
      eventSource.close();
      setStatus('error');
      setMessage('Confirmation timeout. Please check your email for updates.');
    }, 60000);

    // Store timeout ID for cleanup
    return () => {
      clearTimeout(sseTimeout);
      eventSource.close();
    };
  };

  // ============================================================
  // ERROR HANDLER
  // ============================================================
  const handleError = (err: unknown) => {
    console.error('Registration error:', err);

    let errorMessage = 'An unexpected error occurred';

    if (err instanceof TypeError) {
      if (err.message.includes('fetch')) {
        errorMessage = 'Network error. Please check your connection.';
      }
    } else if (err instanceof Error) {
      if (err.name === 'AbortError') {
        errorMessage = 'Request timeout. Please try again.';
      } else {
        errorMessage = err.message;
      }
    }

    setStatus('error');
    setMessage(errorMessage);
  };

  // ============================================================
  // CLEANUP ON UNMOUNT
  // ============================================================
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // ============================================================
  // SUCCESS CONFIRMATION MODAL
  // ============================================================
  if (status === 'success' && showModal && registrationData) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-8 animate-in fade-in zoom-in">
          {/* Success Icon */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <svg
                className="w-8 h-8 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Registration Confirmed!
            </h3>
            <p className="text-gray-600">
              You're all set for {eventTitle}
            </p>
          </div>

          {/* Registration Details */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-3">
            <div className="flex justify-between items-start">
              <span className="text-sm font-medium text-gray-600">Name:</span>
              <span className="text-sm text-gray-900 font-semibold">
                {registrationData.full_name}
              </span>
            </div>
            <div className="flex justify-between items-start">
              <span className="text-sm font-medium text-gray-600">Email:</span>
              <span className="text-sm text-gray-900">
                {registrationData.email}
              </span>
            </div>
            {registrationData.phone && (
              <div className="flex justify-between items-start">
                <span className="text-sm font-medium text-gray-600">Phone:</span>
                <span className="text-sm text-gray-900">
                  {registrationData.phone}
                </span>
              </div>
            )}
            <div className="flex justify-between items-start">
              <span className="text-sm font-medium text-gray-600">Status:</span>
              <span className="inline-block px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                {registrationData.status}
              </span>
            </div>
            <div className="flex justify-between items-start">
              <span className="text-sm font-medium text-gray-600">Confirmation ID:</span>
              <span className="text-xs text-gray-600 font-mono break-all">
                {registrationId}
              </span>
            </div>
          </div>

          {/* Confirmation Message */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-900">
              A confirmation email has been sent to <strong>{registrationData.email}</strong>. 
              Please check your inbox for event details.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => setShowModal(false)}
              className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Close
            </button>
            <button
              onClick={() => window.print()}
              className="w-full bg-gray-200 text-gray-900 py-2 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            >
              Print Confirmation
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ============================================================
  // MAIN FORM RENDER
  // ============================================================
  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {/* Full Name Field */}
      <div>
        <label
          htmlFor="full_name"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Full Name *
        </label>
        <input
          id="full_name"
          type="text"
          placeholder="John Doe"
          required
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
            errors.full_name
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300'
          }`}
          value={form.full_name}
          onChange={(e) => {
            setForm({ ...form, full_name: e.target.value });
            if (errors.full_name) {
              setErrors({ ...errors, full_name: '' });
            }
          }}
          disabled={status === 'submitting' || status === 'processing'}
          aria-invalid={!!errors.full_name}
          aria-describedby={errors.full_name ? 'full_name_error' : undefined}
        />
        {errors.full_name && (
          <p id="full_name_error" className="mt-1 text-sm text-red-600 flex items-center gap-1">
            <span>⚠️</span> {errors.full_name}
          </p>
        )}
      </div>

      {/* Email Field */}
      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Email Address *
        </label>
        <input
          id="email"
          type="email"
          placeholder="john@example.com"
          required
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
            errors.email
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300'
          }`}
          value={form.email}
          onChange={(e) => {
            setForm({ ...form, email: e.target.value });
            if (errors.email) {
              setErrors({ ...errors, email: '' });
            }
          }}
          disabled={status === 'submitting' || status === 'processing'}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email_error' : undefined}
        />
        {errors.email && (
          <p id="email_error" className="mt-1 text-sm text-red-600 flex items-center gap-1">
            <span>⚠️</span> {errors.email}
          </p>
        )}
      </div>

      {/* Phone Field */}
      <div>
        <label
          htmlFor="phone"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Phone Number (Optional)
        </label>
        <input
          id="phone"
          type="tel"
          placeholder="+1 (555) 123-4567"
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
            errors.phone
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300'
          }`}
          value={form.phone}
          onChange={(e) => {
            setForm({ ...form, phone: e.target.value });
            if (errors.phone) {
              setErrors({ ...errors, phone: '' });
            }
          }}
          disabled={status === 'submitting' || status === 'processing'}
          aria-invalid={!!errors.phone}
          aria-describedby={errors.phone ? 'phone_error' : undefined}
        />
        {errors.phone && (
          <p id="phone_error" className="mt-1 text-sm text-red-600 flex items-center gap-1">
            <span>⚠️</span> {errors.phone}
          </p>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={status === 'submitting' || status === 'processing'}
        className={`w-full py-3 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 ${
          status === 'submitting' || status === 'processing'
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 active:scale-95'
        }`}
        aria-busy={status === 'submitting' || status === 'processing'}
      >
        {status === 'submitting' && (
          <>
            <span className="animate-spin">⏳</span> Submitting...
          </>
        )}
        {status === 'processing' && (
          <>
            <span className="animate-spin">⏳</span> Processing...
          </>
        )}
        {status === 'idle' && 'Register Now'}
        {status === 'error' && 'Try Again'}
      </button>

      {/* Error Alert */}
      {status === 'error' && message && (
        <div
          className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex gap-3"
          role="alert"
        >
          <span className="text-xl">❌</span>
          <div>
            <p className="font-medium">Registration Error</p>
            <p className="text-sm">{message}</p>
          </div>
        </div>
      )}

      {/* Processing Alert */}
      {status === 'processing' && message && (
        <div
          className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg flex gap-3"
          role="status"
        >
          <span className="text-xl">ℹ️</span>
          <p className="text-sm">{message}</p>
        </div>
      )}

      {/* Info Text */}
      <p className="text-xs text-gray-500 text-center">
        We'll never share your information. See our privacy policy.
      </p>
    </form>
  );
}