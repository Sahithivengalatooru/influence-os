import { NextRequest, NextResponse } from "next/server";

/**
 * Catch-all proxy for the FastAPI backend.
 * Example:
 *   /api/proxy/health                  -> http://localhost:8000/v1/health
 *   /api/proxy/content/generate        -> http://localhost:8000/v1/content/generate
 *
 * Base URL is taken from:
 *   - NEXT_PUBLIC_API_BASE_URL (preferred)
 *   - API_BASE_URL
 *   - default: http://localhost:8000/v1
 */

function getBase(): string {
  const raw =
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.API_BASE_URL ||
    "http://localhost:8000/v1";
  return raw.replace(/\/+$/, ""); // trim trailing slashes
}

function joinUrl(base: string, parts: string[], search: string): string {
  const path = (parts || []).map(encodeURIComponent).join("/");
  return `${base}/${path}${search || ""}`;
}

async function forward(req: NextRequest, path: string[]) {
  const target = joinUrl(getBase(), path, req.nextUrl.search);

  // Build outbound headers (drop hop-by-hop + unsafe ones)
  const headers: Record<string, string> = {};
  for (const [k, v] of req.headers) {
    const key = k.toLowerCase();
    if (
      key === "host" ||
      key === "content-length" ||
      key === "connection" ||
      key === "accept-encoding" ||
      key === "cookie"
    ) {
      continue;
    }
    headers[k] = v;
  }

  // Only send a body for non-GET/HEAD
  let body: BodyInit | undefined;
  if (!["GET", "HEAD"].includes(req.method)) {
    body = await req.text(); // good for JSON; switch to arrayBuffer for binary
    if (!headers["content-type"]) {
      headers["content-type"] = "application/json";
    }
  }

  try {
    const resp = await fetch(target, {
      method: req.method,
      headers,
      body,
      redirect: "manual",
      cache: "no-store",
    });

    // Copy response headers (drop size/encoding that Next will recompute)
    const outHeaders = new Headers(resp.headers);
    outHeaders.delete("content-encoding");
    outHeaders.delete("transfer-encoding");
    outHeaders.delete("content-length");

    const buf = await resp.arrayBuffer();
    return new NextResponse(buf, {
      status: resp.status,
      headers: outHeaders,
    });
  } catch (err: any) {
    // Return a clear JSON 502 instead of throwing (which causes "Unexpected end of JSON input")
    return NextResponse.json(
      {
        error: "Bad Gateway",
        target,
        detail:
          typeof err?.message === "string"
            ? err.message
            : "Failed to reach backend",
      },
      { status: 502 }
    );
  }
}

/* Handlers for common HTTP verbs */
export async function GET(
  req: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return forward(req, params.path || []);
}
export async function POST(
  req: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return forward(req, params.path || []);
}
export async function PUT(
  req: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return forward(req, params.path || []);
}
export async function DELETE(
  req: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return forward(req, params.path || []);
}
export async function PATCH(
  req: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return forward(req, params.path || []);
}

/* Basic CORS/preflight support (optional) */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,PATCH,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

/* Ensure no caching and Node runtime by default */
export const dynamic = "force-dynamic";
export const runtime = "nodejs";
