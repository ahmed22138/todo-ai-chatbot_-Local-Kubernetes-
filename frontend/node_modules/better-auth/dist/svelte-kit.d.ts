import { A as Auth, a as BetterAuthOptions } from './index-BMranMWG.js';
import 'kysely';
import './index-C8A40nOX.js';
import 'arctic';
import 'zod';
import './helper-C1ihmerM.js';
import 'better-call';

declare const toSvelteKitHandler: (auth: Auth) => (event: {
    request: Request;
}) => Promise<Response>;
declare const svelteKitHandler: ({ auth, event, resolve, }: {
    auth: Auth;
    event: {
        request: Request;
        url: URL;
    };
    resolve: (event: any) => any;
}) => any;
declare function isAuthPath(url: string, options: BetterAuthOptions): boolean;

export { isAuthPath, svelteKitHandler, toSvelteKitHandler };
