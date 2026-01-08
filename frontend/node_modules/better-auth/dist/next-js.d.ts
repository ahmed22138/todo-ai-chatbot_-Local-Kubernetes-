import { A as Auth } from './index-BMranMWG.js';
import { U as User, S as Session } from './index-C8A40nOX.js';
import { NextRequest } from 'next/server';
import 'kysely';
import 'better-call';
import 'zod';
import './helper-C1ihmerM.js';
import 'arctic';

declare function toNextJsHandler(auth: Auth | Auth["handler"]): {
    GET: (request: Request) => Promise<Response>;
    POST: (request: Request) => Promise<Response>;
};
/**
 * Middleware that checks if the user is authenticated.
 * If not, it redirects to the redirectTo URL.
 */
declare function authMiddleware(options: {
    baePath?: string;
    redirectTo?: string;
    customRedirect?: (session: {
        user: User;
        session: Session;
    } | null, request: NextRequest) => Promise<any>;
}): (request: NextRequest) => Promise<any>;

export { authMiddleware, toNextJsHandler };
