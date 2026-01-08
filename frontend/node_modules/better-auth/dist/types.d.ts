import { B as BetterAuthPlugin, A as Auth, m as InferSession, n as InferUser } from './index-BMranMWG.js';
export { t as Adapter, f as AuthContext, a as BetterAuthOptions, G as GenericEndpointContext, H as HookEndpointContext, q as InferPluginTypes, P as PluginSchema, R as RateLimit, S as SessionAdapter, W as Where, r as init } from './index-BMranMWG.js';
import { U as UnionToIntersection, H as HasRequiredKeys, P as Prettify, L as LiteralString } from './helper-C1ihmerM.js';
export { a as LiteralUnion, R as RequiredKeysOf, W as WithoutEmpty } from './helper-C1ihmerM.js';
export { f as OAuthProvider, O as OAuthProviderList, P as ProviderOptions, S as Session, U as User } from './index-C8A40nOX.js';
import { BetterFetchOption, BetterFetchResponse, BetterFetch, BetterFetchPlugin } from '@better-fetch/fetch';
import { Atom } from 'nanostores';
import { Endpoint, Context } from 'better-call';
import 'kysely';
import 'zod';
import 'arctic';

type CamelCase<S extends string> = S extends `${infer P1}-${infer P2}${infer P3}` ? `${Lowercase<P1>}${Uppercase<P2>}${CamelCase<P3>}` : Lowercase<S>;
type PathToObject<T extends string, Fn extends (...args: any[]) => any> = T extends `/${infer Segment}/${infer Rest}` ? {
    [K in CamelCase<Segment>]: PathToObject<`/${Rest}`, Fn>;
} : T extends `/${infer Segment}` ? {
    [K in CamelCase<Segment>]: Fn;
} : never;
type InferCtx<C extends Context<any, any>> = C["body"] extends Record<string, any> ? C["body"] & {
    fetchOptions?: BetterFetchOption<undefined, C["query"], C["params"]>;
} : C["query"] extends Record<string, any> ? {
    query: C["query"];
    fetchOptions?: Omit<BetterFetchOption<C["body"], C["query"], C["params"]>, "query">;
} : {
    fetchOptions?: BetterFetchOption<C["body"], C["query"], C["params"]>;
};
type MergeRoutes<T> = UnionToIntersection<T>;
type InferRoute<API> = API extends {
    [key: string]: infer T;
} ? T extends Endpoint ? T["options"]["metadata"] extends {
    isAction: false;
} ? {} : PathToObject<T["path"], T extends (ctx: infer C) => infer R ? C extends Context<any, any> ? (...data: HasRequiredKeys<InferCtx<C>> extends true ? [
    Prettify<InferCtx<C>>,
    BetterFetchOption<C["body"], C["query"], C["params"]>?
] : [
    Prettify<InferCtx<C>>?,
    BetterFetchOption<C["body"], C["query"], C["params"]>?
]) => Promise<BetterFetchResponse<Awaited<R>>> : never : never> : never : never;
type InferRoutes<API extends Record<string, Endpoint>> = MergeRoutes<InferRoute<API>>;

type AtomListener = {
    matcher: (path: string) => boolean;
    signal: string;
};
interface BetterAuthClientPlugin {
    id: LiteralString;
    /**
     * only used for type inference. don't pass the
     * actual plugin
     */
    $InferServerPlugin?: BetterAuthPlugin;
    /**
     * Custom actions
     */
    getActions?: ($fetch: BetterFetch) => Record<string, any>;
    /**
     * State atoms that'll be resolved by each framework
     * auth store.
     */
    getAtoms?: ($fetch: BetterFetch) => Record<string, Atom<any>>;
    /**
     * specify path methods for server plugin inferred
     * endpoints to force a specific method.
     */
    pathMethods?: Record<string, "POST" | "GET">;
    /**
     * Better fetch plugins
     */
    fetchPlugins?: BetterFetchPlugin[];
    /**
     * a list of recaller based on a matcher function.
     * The signal name needs to match a signal in this
     * plugin or any plugin the user might have added.
     */
    atomListeners?: AtomListener[];
}
interface ClientOptions {
    fetchOptions?: BetterFetchOption;
    plugins?: BetterAuthClientPlugin[];
    baseURL?: string;
}
type InferClientAPI<O extends ClientOptions> = InferRoutes<O["plugins"] extends Array<any> ? (O["plugins"] extends Array<infer Pl> ? UnionToIntersection<Pl extends {
    $InferServerPlugin: infer Plug;
} ? Plug extends BetterAuthPlugin ? Plug["endpoints"] : {} : {}> : {}) & Auth["api"] : Auth["api"]>;
type InferActions<O extends ClientOptions> = O["plugins"] extends Array<infer Plugin> ? UnionToIntersection<Plugin extends BetterAuthClientPlugin ? Plugin["getActions"] extends ($fetch: BetterFetch) => infer Actions ? Actions : {} : {}> : {};
/**
 * signals are just used to recall a computed value. as a
 * convention they start with "_"
 */
type IsSignal<T> = T extends `_${infer _}` ? true : false;
type InferPluginsFromClient<O extends ClientOptions> = O["plugins"] extends Array<BetterAuthClientPlugin> ? Array<O["plugins"][number]["$InferServerPlugin"]> : undefined;
type InferAuthFromClient<O extends ClientOptions> = {
    handler: any;
    api: any;
    options: {
        database: any;
        plugins: InferPluginsFromClient<O>;
    };
};
type InferSessionFromClient<O extends ClientOptions> = InferSession<InferAuthFromClient<O> extends Auth ? InferAuthFromClient<O> : never>;
type InferUserFromClient<O extends ClientOptions> = InferUser<InferAuthFromClient<O> extends Auth ? InferAuthFromClient<O> : never>;

export { type AtomListener, type BetterAuthClientPlugin, BetterAuthPlugin, type ClientOptions, HasRequiredKeys, type InferActions, type InferClientAPI, type InferPluginsFromClient, InferSession, type InferSessionFromClient, InferUser, type InferUserFromClient, type IsSignal, LiteralString, Prettify, UnionToIntersection };
