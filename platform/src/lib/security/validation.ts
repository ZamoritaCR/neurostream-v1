import validator from "validator";

/**
 * Input validation and sanitization utilities.
 *
 * Research: Brain 4, Section 10 - ADHD-friendly error messaging
 * Security: OWASP Input Validation Cheat Sheet
 */

/** Sanitize user text input - strip HTML tags, trim whitespace */
export function sanitizeInput(input: string): string {
  return validator.stripLow(validator.trim(input));
}

/** Validate email format */
export function isValidEmail(email: string): boolean {
  return validator.isEmail(email);
}

/** Validate chat message - non-empty, within length bounds */
export function isValidMessage(
  message: string,
  maxLength: number = 2000
): boolean {
  const trimmed = message.trim();
  return trimmed.length > 0 && trimmed.length <= maxLength;
}

/** Sanitize a string for safe display (escape HTML entities) */
export function escapeForDisplay(input: string): string {
  return validator.escape(input);
}

/** Validate that a string is a safe URL (http/https only) */
export function isValidUrl(url: string): boolean {
  return validator.isURL(url, {
    protocols: ["http", "https"],
    require_protocol: true,
  });
}

/** Validate a mood/presence state string against allowed values */
export function isValidMoodState(
  state: string,
  allowed: string[]
): boolean {
  return allowed.includes(state);
}

/** Validate password strength */
export function validatePassword(password: string): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (!password || typeof password !== "string") {
    return { valid: false, errors: ["Password is required"] };
  }
  if (password.length < 8) {
    errors.push("Password must be at least 8 characters");
  }
  if (password.length > 128) {
    errors.push("Password must be less than 128 characters");
  }
  if (!/[a-z]/.test(password)) {
    errors.push("Password must contain a lowercase letter");
  }
  if (!/[A-Z]/.test(password)) {
    errors.push("Password must contain an uppercase letter");
  }
  if (!/[0-9]/.test(password)) {
    errors.push("Password must contain a number");
  }

  return { valid: errors.length === 0, errors };
}

/** Validate age for COPPA compliance (must be 13+) */
export function validateAge(birthDate: Date): {
  valid: boolean;
  age: number;
  error?: string;
} {
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }

  if (age < 13) {
    return { valid: false, age, error: "You must be at least 13 years old (COPPA requirement)" };
  }
  if (age > 120) {
    return { valid: false, age, error: "Invalid birth date" };
  }

  return { valid: true, age };
}

/** Validate content length within bounds */
export function validateContentLength(
  content: string,
  min: number,
  max: number
): { valid: boolean; error?: string } {
  if (!content || typeof content !== "string") {
    return { valid: false, error: "Content is required" };
  }
  if (content.length < min) {
    return { valid: false, error: `Content must be at least ${min} characters` };
  }
  if (content.length > max) {
    return { valid: false, error: `Content must be less than ${max} characters` };
  }
  return { valid: true };
}
