import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

// ⚡ FIX: Removed '/' from public routes so the home page gets locked!
const isPublicRoute = createRouteMatcher(['/sign-in(.*)', '/sign-up(.*)']);

// ⚡ FIX: Added 'async' here and 'await' before auth.protect()
export default clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};