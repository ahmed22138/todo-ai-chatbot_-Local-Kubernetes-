import { A as Auth } from './index-BMranMWG.js';
import 'kysely';
import './index-C8A40nOX.js';
import 'arctic';
import 'zod';
import './helper-C1ihmerM.js';
import 'better-call';

declare function toSolidStartHandler(auth: Auth | Auth["handler"]): {
    GET: (event: {
        request: Request;
    }) => Promise<Response>;
    POST: (event: {
        request: Request;
    }) => Promise<Response>;
};

export { toSolidStartHandler };
