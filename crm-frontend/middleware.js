import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

// Define protected and auth routes
const protectedRoutes = ['/dashboard'];
const authRoutes = ['/login', '/register', '/forgot-password'];

export async function middleware(request) {
  const { pathname } = request.nextUrl;
  
  // Check if the route is protected
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));
  const isAuthRoute = authRoutes.some(route => pathname.startsWith(route));

  // Get the access token from cookies
  const cookieStore = cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  // If trying to access protected route without token, redirect to login
  if (isProtectedRoute && !accessToken) {
    const url = new URL('/login', request.url);
    url.searchParams.set('callbackUrl', encodeURI(pathname));
    return NextResponse.redirect(url);
  }

  // If trying to access auth routes with valid token, redirect to dashboard
  if (isAuthRoute && accessToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};