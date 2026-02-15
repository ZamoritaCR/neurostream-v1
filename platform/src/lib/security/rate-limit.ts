/**
 * Simple in-memory rate limiter for API routes.
 *
 * For production at scale, replace with Redis-backed solution.
 * This works well for Vercel serverless with moderate traffic.
 */

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

const rateLimitMap = new Map<string, RateLimitEntry>();

// Clean up expired entries every 5 minutes
setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of rateLimitMap) {
    if (now > entry.resetTime) {
      rateLimitMap.delete(key);
    }
  }
}, 5 * 60 * 1000);

interface RateLimitOptions {
  /** Max requests allowed in the window */
  maxRequests: number;
  /** Time window in seconds */
  windowSeconds: number;
}

interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetIn: number;
}

/**
 * Check rate limit for a given identifier (IP, user ID, etc.)
 *
 * Usage in API route:
 *   const ip = request.headers.get("x-forwarded-for") || "unknown";
 *   const limit = checkRateLimit(ip, { maxRequests: 10, windowSeconds: 60 });
 *   if (!limit.allowed) return NextResponse.json({ error: "Too many requests" }, { status: 429 });
 */
export function checkRateLimit(
  identifier: string,
  options: RateLimitOptions
): RateLimitResult {
  const now = Date.now();
  const key = identifier;
  const entry = rateLimitMap.get(key);

  if (!entry || now > entry.resetTime) {
    rateLimitMap.set(key, {
      count: 1,
      resetTime: now + options.windowSeconds * 1000,
    });
    return {
      allowed: true,
      remaining: options.maxRequests - 1,
      resetIn: options.windowSeconds,
    };
  }

  entry.count += 1;

  if (entry.count > options.maxRequests) {
    return {
      allowed: false,
      remaining: 0,
      resetIn: Math.ceil((entry.resetTime - now) / 1000),
    };
  }

  return {
    allowed: true,
    remaining: options.maxRequests - entry.count,
    resetIn: Math.ceil((entry.resetTime - now) / 1000),
  };
}

/** Preset rate limit configurations for common endpoints */
export const RATE_LIMITS = {
  /** Auth endpoints - strict: 5 per 15 min */
  AUTH_ATTEMPT: { maxRequests: 5, windowSeconds: 15 * 60 },
  /** AI generation - moderate: 10 per hour */
  AI_GENERATION: { maxRequests: 10, windowSeconds: 60 * 60 },
  /** General API - lenient: 100 per minute */
  GENERAL_API: { maxRequests: 100, windowSeconds: 60 },
  /** Chat messages - moderate: 30 per minute */
  CHAT_MESSAGE: { maxRequests: 30, windowSeconds: 60 },
} as const;
