import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse, type NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const next = searchParams.get("next") || "/watch";

  if (code) {
    const cookieStore = await cookies();

    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll();
          },
          setAll(cookiesToSet) {
            try {
              cookiesToSet.forEach(({ name, value, options }) =>
                cookieStore.set(name, value, options)
              );
            } catch {
              // setAll called from Server Component — middleware handles refresh
            }
          },
        },
      }
    );

    try {
      const { data, error } = await supabase.auth.exchangeCodeForSession(code);

      if (error) {
        console.error("Session exchange error:", error.message);
        return NextResponse.redirect(new URL("/auth", origin));
      }

      if (data.session) {
        return NextResponse.redirect(new URL(next, origin));
      }
    } catch (err: unknown) {
      console.error(
        "Callback error:",
        err instanceof Error ? err.message : err
      );
    }
  }

  // No code or exchange failed — redirect to auth
  // Client-side Supabase will handle hash-based tokens
  return NextResponse.redirect(new URL("/auth", origin));
}
