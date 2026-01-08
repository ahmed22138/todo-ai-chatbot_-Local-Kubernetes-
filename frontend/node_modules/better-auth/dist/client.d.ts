import * as zod from 'zod';
import * as nanostores from 'nanostores';
import { PreinitializedWritableAtom } from 'nanostores';
import * as _better_fetch_fetch from '@better-fetch/fetch';
import { BetterFetch, BetterFetchError, BetterFetchOption } from '@better-fetch/fetch';
import { B as BetterAuthPlugin, F as FieldAttribute, I as InferFieldOutput } from './index-BMranMWG.js';
import { U as UnionToIntersection, P as Prettify } from './helper-C1ihmerM.js';
import { ClientOptions, InferClientAPI, InferActions, BetterAuthClientPlugin, InferSessionFromClient, InferUserFromClient, IsSignal } from './types.js';
export { AtomListener, InferPluginsFromClient } from './types.js';
import 'kysely';
import './index-C8A40nOX.js';
import 'arctic';
import 'better-call';

type InferResolvedHooks<O extends ClientOptions> = O["plugins"] extends Array<infer Plugin> ? Plugin extends BetterAuthClientPlugin ? Plugin["getAtoms"] extends (fetch: any) => infer Atoms ? Atoms extends Record<string, any> ? {
    [key in keyof Atoms as IsSignal<key> extends true ? never : key extends string ? `use${Capitalize<key>}` : never]: Atoms[key];
} : {} : {} : {} : {};
declare function createAuthClient<Option extends ClientOptions>(options?: Option): UnionToIntersection<InferResolvedHooks<Option>> & InferClientAPI<Option> & InferActions<Option> & {
    useSession: nanostores.PreinitializedWritableAtom<{
        data: {
            user: Prettify<UnionToIntersection<{
                id: string;
                email: string;
                emailVerified: boolean;
                name: string;
                createdAt: Date;
                updatedAt: Date;
                image?: string | undefined;
            } & ((Option["plugins"] extends BetterAuthClientPlugin[] ? (Option["plugins"][number] extends infer T ? T extends BetterAuthClientPlugin ? T["$InferServerPlugin"] extends infer U ? U extends BetterAuthPlugin ? U : never : never : never : never)[] : never) extends (infer T_1)[] ? T_1 extends {
                schema: {
                    user: {
                        fields: infer Field;
                    };
                };
            } ? Field extends Record<infer Key extends string | number | symbol, FieldAttribute> ? Prettify<{ [key in Key as Field[key]["required"] extends false ? never : Field[key]["defaultValue"] extends string | number | boolean | Function | Date ? key : never]: InferFieldOutput<Field[key]>; } & { [key_1 in Key as Field[key_1]["returned"] extends false ? never : key_1]?: InferFieldOutput<Field[key_1]> | undefined; }> : {} : {} : {})>>;
            session: Prettify<UnionToIntersection<{
                id: string;
                userId: string;
                expiresAt: Date;
                ipAddress?: string | undefined;
                userAgent?: string | undefined;
            } & ((Option["plugins"] extends BetterAuthClientPlugin[] ? (Option["plugins"][number] extends infer T ? T extends BetterAuthClientPlugin ? T["$InferServerPlugin"] extends infer U ? U extends BetterAuthPlugin ? U : never : never : never : never)[] : never) extends (infer T_2)[] ? T_2 extends {
                schema: {
                    session: {
                        fields: infer Field_1;
                    };
                };
            } ? Field_1 extends Record<string, FieldAttribute> ? { [key_2 in keyof Field_1]: InferFieldOutput<Field_1[key_2]>; } : {} : {} : {})>>;
        } | null;
        error: null | _better_fetch_fetch.BetterFetchError;
        isPending: boolean;
    }>;
    $fetch: _better_fetch_fetch.BetterFetch<{
        plugins: (_better_fetch_fetch.BetterFetchPlugin | {
            id: string;
            name: string;
            hooks: {
                onSuccess(context: _better_fetch_fetch.SuccessContext<any>): void;
            };
        } | {
            id: string;
            name: string;
            hooks: {
                onRequest<T_3 extends Record<string, any>>(context: _better_fetch_fetch.RequestContext<T_3>): _better_fetch_fetch.RequestContext<T_3>;
            };
        } | {
            id: string;
            name: string;
            init(url: string, options: {
                headers?: (HeadersInit & (HeadersInit | {
                    accept: "application/json" | "text/plain" | "application/octet-stream";
                    "content-type": "application/json" | "text/plain" | "application/x-www-form-urlencoded" | "multipart/form-data" | "application/octet-stream";
                    authorization: "Bearer" | "Basic";
                })) | undefined;
                redirect?: RequestRedirect | undefined;
                method?: string | undefined;
                cache?: RequestCache | undefined;
                credentials?: RequestCredentials | undefined;
                integrity?: string | undefined;
                keepalive?: boolean | undefined;
                mode?: RequestMode | undefined;
                priority?: RequestPriority | undefined;
                referrer?: string | undefined;
                referrerPolicy?: ReferrerPolicy | undefined;
                signal?: (AbortSignal | null) | undefined;
                window?: null | undefined;
                onRequest?: (<T_3 extends Record<string, any>>(context: _better_fetch_fetch.RequestContext<T_3>) => Promise<_better_fetch_fetch.RequestContext | void> | _better_fetch_fetch.RequestContext | void) | undefined;
                onResponse?: ((context: _better_fetch_fetch.ResponseContext) => Promise<Response | void | _better_fetch_fetch.ResponseContext> | Response | _better_fetch_fetch.ResponseContext | void) | undefined;
                onSuccess?: ((context: _better_fetch_fetch.SuccessContext<any>) => Promise<void> | void) | undefined;
                onError?: ((context: _better_fetch_fetch.ErrorContext) => Promise<void> | void) | undefined;
                onRetry?: ((response: _better_fetch_fetch.ResponseContext) => Promise<void> | void) | undefined;
                hookOptions?: {
                    cloneResponse?: boolean;
                } | undefined;
                timeout?: number | undefined;
                customFetchImpl?: _better_fetch_fetch.FetchEsque | undefined;
                plugins?: _better_fetch_fetch.BetterFetchPlugin[] | undefined;
                baseURL?: string | undefined;
                throw?: boolean | undefined;
                auth?: ({
                    type: "Bearer";
                    token: string | (() => string | undefined) | undefined;
                } | {
                    type: "Basic";
                    username: string | (() => string | undefined) | undefined;
                    password: string | (() => string | undefined) | undefined;
                } | {
                    type: "Custom";
                    prefix: string | (() => string | undefined) | undefined;
                    value: string | (() => string | undefined) | undefined;
                }) | undefined;
                body?: any;
                query?: any;
                params?: any;
                duplex?: ("full" | "half") | undefined;
                jsonParser?: (<T_3>(text: string) => Promise<T_3 | undefined>) | undefined;
                retry?: (number | {
                    type: "linear";
                    attempts: number;
                    delay: number;
                    shouldRetry?: (response: Response | null) => boolean | Promise<boolean>;
                } | {
                    type: "exponential";
                    attempts: number;
                    baseDelay: number;
                    maxDelay: number;
                    shouldRetry?: (response: Response | null) => boolean | Promise<boolean>;
                }) | undefined;
                retryAttempt?: number | undefined;
                output?: (zod.ZodType | typeof Blob | typeof File) | undefined;
                errorSchema?: zod.ZodType | undefined;
                disableValidation?: boolean | undefined;
            } | undefined): Promise<Response | {
                url: string;
                options: {
                    headers?: (HeadersInit & (HeadersInit | {
                        accept: "application/json" | "text/plain" | "application/octet-stream";
                        "content-type": "application/json" | "text/plain" | "application/x-www-form-urlencoded" | "multipart/form-data" | "application/octet-stream";
                        authorization: "Bearer" | "Basic";
                    })) | undefined;
                    redirect?: RequestRedirect | undefined;
                    method?: string | undefined;
                    cache?: RequestCache | undefined;
                    credentials?: RequestCredentials | undefined;
                    integrity?: string | undefined;
                    keepalive?: boolean | undefined;
                    mode?: RequestMode | undefined;
                    priority?: RequestPriority | undefined;
                    referrer?: string | undefined;
                    referrerPolicy?: ReferrerPolicy | undefined;
                    signal?: (AbortSignal | null) | undefined;
                    window?: null | undefined;
                    onRequest?: (<T_3 extends Record<string, any>>(context: _better_fetch_fetch.RequestContext<T_3>) => Promise<_better_fetch_fetch.RequestContext | void> | _better_fetch_fetch.RequestContext | void) | undefined;
                    onResponse?: ((context: _better_fetch_fetch.ResponseContext) => Promise<Response | void | _better_fetch_fetch.ResponseContext> | Response | _better_fetch_fetch.ResponseContext | void) | undefined;
                    onSuccess?: ((context: _better_fetch_fetch.SuccessContext<any>) => Promise<void> | void) | undefined;
                    onError?: ((context: _better_fetch_fetch.ErrorContext) => Promise<void> | void) | undefined;
                    onRetry?: ((response: _better_fetch_fetch.ResponseContext) => Promise<void> | void) | undefined;
                    hookOptions?: {
                        cloneResponse?: boolean;
                    } | undefined;
                    timeout?: number | undefined;
                    customFetchImpl?: _better_fetch_fetch.FetchEsque | undefined;
                    plugins?: _better_fetch_fetch.BetterFetchPlugin[] | undefined;
                    baseURL?: string | undefined;
                    throw?: boolean | undefined;
                    auth?: ({
                        type: "Bearer";
                        token: string | (() => string | undefined) | undefined;
                    } | {
                        type: "Basic";
                        username: string | (() => string | undefined) | undefined;
                        password: string | (() => string | undefined) | undefined;
                    } | {
                        type: "Custom";
                        prefix: string | (() => string | undefined) | undefined;
                        value: string | (() => string | undefined) | undefined;
                    }) | undefined;
                    body?: any;
                    query?: any;
                    params?: any;
                    duplex?: ("full" | "half") | undefined;
                    jsonParser?: (<T_3>(text: string) => Promise<T_3 | undefined>) | undefined;
                    retry?: (number | {
                        type: "linear";
                        attempts: number;
                        delay: number;
                        shouldRetry?: (response: Response | null) => boolean | Promise<boolean>;
                    } | {
                        type: "exponential";
                        attempts: number;
                        baseDelay: number;
                        maxDelay: number;
                        shouldRetry?: (response: Response | null) => boolean | Promise<boolean>;
                    }) | undefined;
                    retryAttempt?: number | undefined;
                    output?: (zod.ZodType | typeof Blob | typeof File) | undefined;
                    errorSchema?: zod.ZodType | undefined;
                    disableValidation?: boolean | undefined;
                };
            }>;
        })[];
        headers?: (HeadersInit & (HeadersInit | {
            accept: "application/json" | "text/plain" | "application/octet-stream";
            "content-type": "application/json" | "text/plain" | "application/x-www-form-urlencoded" | "multipart/form-data" | "application/octet-stream";
            authorization: "Bearer" | "Basic";
        })) | undefined;
        redirect?: RequestRedirect;
        method?: string;
        cache?: RequestCache;
        credentials: RequestCredentials;
        integrity?: string;
        keepalive?: boolean;
        mode?: RequestMode;
        priority?: RequestPriority;
        referrer?: string;
        referrerPolicy?: ReferrerPolicy;
        signal?: AbortSignal | null;
        window?: null;
        onRequest?: <T_3 extends Record<string, any>>(context: _better_fetch_fetch.RequestContext<T_3>) => Promise<_better_fetch_fetch.RequestContext | void> | _better_fetch_fetch.RequestContext | void;
        onResponse?: (context: _better_fetch_fetch.ResponseContext) => Promise<Response | void | _better_fetch_fetch.ResponseContext> | Response | _better_fetch_fetch.ResponseContext | void;
        onSuccess?: ((context: _better_fetch_fetch.SuccessContext<any>) => Promise<void> | void) | undefined;
        onError?: (context: _better_fetch_fetch.ErrorContext) => Promise<void> | void;
        onRetry?: (response: _better_fetch_fetch.ResponseContext) => Promise<void> | void;
        hookOptions?: {
            cloneResponse?: boolean;
        };
        timeout?: number;
        customFetchImpl?: _better_fetch_fetch.FetchEsque;
        baseURL: string;
        throw?: boolean;
        auth?: {
            type: "Bearer";
            token: string | (() => string | undefined) | undefined;
        } | {
            type: "Basic";
            username: string | (() => string | undefined) | undefined;
            password: string | (() => string | undefined) | undefined;
        } | {
            type: "Custom";
            prefix: string | (() => string | undefined) | undefined;
            value: string | (() => string | undefined) | undefined;
        };
        body?: any;
        query?: any;
        params?: any;
        duplex?: "full" | "half";
        jsonParser?: <T_3>(text: string) => Promise<T_3 | undefined>;
        retry?: number | {
            type: "linear";
            attempts: number;
            delay: number;
            shouldRetry?: (response: Response | null) => boolean | Promise<boolean>;
        } | {
            type: "exponential";
            attempts: number;
            baseDelay: number;
            maxDelay: number;
            shouldRetry?: (response: Response | null) => boolean | Promise<boolean>;
        };
        retryAttempt?: number;
        output?: zod.ZodType | typeof Blob | typeof File;
        errorSchema?: zod.ZodType;
        disableValidation?: boolean;
    }, unknown, unknown, {}>;
    $Infer: {
        Session: {
            session: InferSessionFromClient<Option>;
            user: InferUserFromClient<Option>;
        };
    };
};

declare const useAuthQuery: <T>(initializedAtom: PreinitializedWritableAtom<any> | PreinitializedWritableAtom<any>[], path: string, $fetch: BetterFetch, options?: ((value: {
    data: null | T;
    error: null | BetterFetchError;
    isPending: boolean;
}) => BetterFetchOption) | BetterFetchOption) => PreinitializedWritableAtom<{
    data: null | T;
    error: null | BetterFetchError;
    isPending: boolean;
}>;

export { BetterAuthClientPlugin, ClientOptions, InferActions, InferClientAPI, InferSessionFromClient, InferUserFromClient, IsSignal, createAuthClient, useAuthQuery };
