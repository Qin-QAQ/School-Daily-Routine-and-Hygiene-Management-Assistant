export function createFetcher(opts = {}) {
  const {
    baseURL = '',
    timeout = 8000,
    retries = 0,
    retryDelay = 500,
    defaultHeaders = { 'Content-Type': 'application/json' },
    getToken = () => null,
    requestInterceptors = [],
    responseInterceptors = [],
    onError = null,
  } = opts;

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  async function applyRequestInterceptors(config) {
    let c = { ...config };
    for (const fn of requestInterceptors) {
      c = (await fn(c)) || c;
    }
    return c;
  }

  async function applyResponseInterceptors(res) {
    let r = res;
    for (const fn of responseInterceptors) {
      r = (await fn(r)) || r;
    }
    return r;
  }

  async function request(method, url, options = {}) {
    const cfg = await applyRequestInterceptors({ method, url, options });
    const { params, body, headers = {}, signal: externalSignal } = cfg.options || {};

    let fullUrl = url.startsWith('http') ? url : baseURL + url;
    if (params) {
      const qs = new URLSearchParams(params).toString();
      if (qs) fullUrl += (fullUrl.includes('?') ? '&' : '?') + qs;
    }

    const token = getToken && getToken();
    const mergedHeaders = { ...defaultHeaders, ...headers };
    if (token) mergedHeaders['Authorization'] = token;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    const signal = externalSignal || controller.signal;

    let attempt = 0;
    while (true) {
      try {
        const res = await fetch(fullUrl, {
          method,
          headers: mergedHeaders,
          body: body != null && !(body instanceof FormData) ? JSON.stringify(body) : body,
          signal,
        });
        clearTimeout(timeoutId);

        const contentType = res.headers.get('content-type') || '';
        let data = null;
        if (contentType.includes('application/json')) {
          data = await res.json();
        } else {
          data = await res.text();
        }

        const wrapped = { ok: res.ok, status: res.status, statusText: res.statusText, headers: res.headers, data };
        const final = await applyResponseInterceptors(wrapped);

        if (!res.ok) {
          const err = new Error(final.data && final.data.message ? final.data.message : res.statusText || 'HTTP Error');
          err.status = res.status;
          err.response = final;
          if (onError) onError(err);
          throw err;
        }
        return final;
      } catch (err) {
        clearTimeout(timeoutId);
        if (err.name === 'AbortError') {
          const ae = new Error('Request timed out or aborted');
          ae.cause = err;
          if (onError) onError(ae);
          throw ae;
        }
        if (attempt < retries) {
          attempt += 1;
          await sleep(retryDelay);
          continue;
        }
        if (onError) onError(err);
        throw err;
      }
    }
  }

  return {
    request,
    get: (url, opts) => request('GET', url, opts),
    post: (url, opts) => request('POST', url, opts),
    put: (url, opts) => request('PUT', url, opts),
    del: (url, opts) => request('DELETE', url, opts),
  };
}

export const fetcher = createFetcher();
