import { f as AuthContext, G as GenericEndpointContext } from './index-BMranMWG.js';
export { i as BetterAuthCookies, h as createCookieGetter, k as createLogger, j as deleteSessionCookie, g as getCookies, l as logger, p as parseSetCookieHeader, s as setSessionCookie } from './index-BMranMWG.js';
export { H as HIDE_METADATA } from './hide-metadata-DEHJp1rk.js';
import { z } from 'zod';
import 'kysely';
import './index-C8A40nOX.js';
import 'arctic';
import './helper-C1ihmerM.js';
import 'better-call';

declare const shimContext: <T extends Record<string, any>>(originalObject: T, newContext: Record<string, any>) => T;
declare const shimEndpoint: (ctx: AuthContext, value: any) => (context: any) => Promise<any>;

declare function getBaseURL(url?: string, path?: string): string | undefined;

declare const clone: <T extends object>(object: T) => T;

declare const getDate: (span: number, isSeconds?: boolean) => Date;

declare function getIp(req: Request): string | null;

declare const generateId: () => string;

declare const merge: (objects: object[]) => object;

declare function capitalizeFirstLetter(str: string): string;

declare function validatePassword(ctx: GenericEndpointContext, data: {
    password: string;
    userId: string;
}): Promise<boolean>;

declare function generateState(callbackURL?: string, currentURL?: string, dontRememberMe?: boolean): {
    state: string;
    code: string;
};
declare function parseState(state: string): z.SafeParseReturnType<{
    code: string;
    currentURL?: string | undefined;
    callbackURL?: string | undefined;
    dontRememberMe?: boolean | undefined;
}, {
    code: string;
    currentURL?: string | undefined;
    callbackURL?: string | undefined;
    dontRememberMe?: boolean | undefined;
}>;

export { capitalizeFirstLetter, clone, generateId, generateState, getBaseURL, getDate, getIp, merge, parseState, shimContext, shimEndpoint, validatePassword };
