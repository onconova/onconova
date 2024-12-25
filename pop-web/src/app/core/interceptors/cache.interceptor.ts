import { Injectable, Inject, Optional, InjectionToken} from '@angular/core';
import {
    HttpInterceptorFn,
    HttpRequest,
    HttpResponse,
    HttpHandlerFn,
    HttpEvent,
  } from '@angular/common/http';
  import { 
    Subject, 
    Observable, 
    finalize, 
    of, 
    tap 
} from 'rxjs';
  
export const CACHE_OPTIONS = new InjectionToken<CacheOptions>('CacheOptions');

  const requests = new Map<
    string,
    {
      src: string;
      data: any;
      data$: any;
      params?: any;
      ttl?: number;
    }
  >();
  
  interface CacheOptions {
    urlsNotToCache?: string[];
    ttls?: { [url: string]: number };
    globalTTL?: number;
  }
  
export const httpCacheInterceptor: HttpInterceptorFn = (request: HttpRequest<any>, next: HttpHandlerFn) => {
  const options: CacheOptions = {};

  const { urlsNotToCache = [] } = options ?? {};
  const skipCache = urlsNotToCache.some((x) => new RegExp(x).test(request.url));

  if (!skipCache) {
    const key = getUniqueKey(request);
    const prevRequest = requests.get(key);

    if (prevRequest) {
      const { data, data$, ttl } = prevRequest;

      if (!data$.closed) {
        return data$.asObservable();
      }

      if (data && ttl && ttl > new Date().getTime()) {
        return of(data);
      }
    } else {
      const data$ = new Subject<HttpEvent<unknown>>();
      requests.set(key, {
        src: request.url,
        data$,
        data: null,
        params: request.body,
        ttl: getTTL(request.url, options),
      });

      return next(request).pipe(
        tap((x) => {
          if (x instanceof HttpResponse) {
            const r = requests.get(key);
            if (r) {
              r.data = x;
              r.ttl = getTTL(request.url, options);
              !r.data$.closed && r.data$.next(x);
            }
          }
        }),
        finalize(() => {
          const r = requests.get(key);
          r?.data$.complete();
          r?.data$.unsubscribe();
        })
      );
    }
  }

  return next(request);
  }
  
function getUniqueKey(req: HttpRequest<unknown>): string {
  const bodySorted = sortObjectByKeys(req.body);
  const key = `${req.method}_${
    req.url
  }_${req.params.toString()}_${JSON.stringify(bodySorted)}`;

  return key;
}

function sortObjectByKeys(obj: any): any {
  const keysSorted = Object.keys(obj  ?? '').sort();
  const objSorted = keysSorted.reduce((_obj, key) => {
    const val = obj[key];
    _obj[key] = typeof val === 'object' ? sortObjectByKeys(val) : val;
    
    return _obj;
  }, {} as any);

  return objSorted;
}

function getTTL(reqUrl: string, options?: CacheOptions): number {
  const { ttls, globalTTL } = options ?? {};

  const getCustomTTL = () => {
    const matchedKey = Object.keys(ttls ?? '').find((x) =>
      reqUrl.split('?')[0].endsWith(x),
    );

    if (!ttls || !matchedKey) {
      return null;
    }

    return ttls[matchedKey];
  };

  return new Date().getTime() + (getCustomTTL() || globalTTL || 0);
}