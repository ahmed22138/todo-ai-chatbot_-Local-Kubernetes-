export { O as OrganizationOptions, b as Passkey, P as PasskeyOptions, W as WebAuthnCookieType, g as getPasskeyActions, o as organization, p as passkey, c as passkeyClient, t as twoFactor, a as twoFactorClient, u as username } from './index-D-u2S_Fl.js';
export { i as ac } from './index-D6NOkCRo.js';
import { H as HookEndpointContext } from './index-BMranMWG.js';
export { d as AuthEndpoint, e as AuthMiddleware, B as BetterAuthPlugin, P as PluginSchema, b as createAuthEndpoint, c as createAuthMiddleware, o as optionsMiddleware } from './index-BMranMWG.js';
export { H as HIDE_METADATA } from './hide-metadata-DEHJp1rk.js';
import * as better_call from 'better-call';
import { z } from 'zod';
import './index-C8A40nOX.js';
import 'arctic';
import './helper-C1ihmerM.js';
import './statement-CU-fdHXK.js';
import '@better-fetch/fetch';
import 'nanostores';
import '@simplewebauthn/types';
import 'kysely';

/**
 * Converts bearer token to session cookie
 */
declare const bearer: () => {
    id: "bearer";
    hooks: {
        before: {
            matcher(context: HookEndpointContext): boolean;
            handler: (ctx: HookEndpointContext) => Promise<void>;
        }[];
    };
};

interface MagicLinkOptions {
    /**
     * Time in seconds until the magic link expires.
     * @default (60 * 5) // 5 minutes
     */
    expiresIn?: number;
    /**
     * Send magic link implementation.
     */
    sendMagicLink: (data: {
        email: string;
        url: string;
        token: string;
    }) => Promise<void> | void;
}
declare const magicLink: (options: MagicLinkOptions) => {
    id: "magic-link";
    endpoints: {
        signInMagicLink: {
            (ctx_0: better_call.Context<"/sign-in/magic-link", {
                method: "POST";
                requireHeaders: true;
                body: z.ZodObject<{
                    email: z.ZodString;
                    callbackURL: z.ZodOptional<z.ZodString>;
                    currentURL: z.ZodOptional<z.ZodString>;
                }, "strip", z.ZodTypeAny, {
                    email: string;
                    currentURL?: string | undefined;
                    callbackURL?: string | undefined;
                }, {
                    email: string;
                    currentURL?: string | undefined;
                    callbackURL?: string | undefined;
                }>;
            }>): Promise<{
                status: boolean;
            }>;
            path: "/sign-in/magic-link";
            options: {
                method: "POST";
                requireHeaders: true;
                body: z.ZodObject<{
                    email: z.ZodString;
                    callbackURL: z.ZodOptional<z.ZodString>;
                    currentURL: z.ZodOptional<z.ZodString>;
                }, "strip", z.ZodTypeAny, {
                    email: string;
                    currentURL?: string | undefined;
                    callbackURL?: string | undefined;
                }, {
                    email: string;
                    currentURL?: string | undefined;
                    callbackURL?: string | undefined;
                }>;
            };
            method: better_call.Method | better_call.Method[];
            headers: Headers;
        };
        magicLinkVerify: {
            (ctx_0: better_call.Context<"/magic-link/verify", {
                method: "GET";
                query: z.ZodObject<{
                    token: z.ZodString;
                    callbackURL: z.ZodOptional<z.ZodString>;
                }, "strip", z.ZodTypeAny, {
                    token: string;
                    callbackURL?: string | undefined;
                }, {
                    token: string;
                    callbackURL?: string | undefined;
                }>;
                requireHeaders: true;
            }>): Promise<{
                status: boolean;
            } | null>;
            path: "/magic-link/verify";
            options: {
                method: "GET";
                query: z.ZodObject<{
                    token: z.ZodString;
                    callbackURL: z.ZodOptional<z.ZodString>;
                }, "strip", z.ZodTypeAny, {
                    token: string;
                    callbackURL?: string | undefined;
                }, {
                    token: string;
                    callbackURL?: string | undefined;
                }>;
                requireHeaders: true;
            };
            method: better_call.Method | better_call.Method[];
            headers: Headers;
        };
    };
};

export { bearer, magicLink };
