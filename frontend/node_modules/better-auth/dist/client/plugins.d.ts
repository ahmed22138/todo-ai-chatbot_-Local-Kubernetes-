import * as nanostores from 'nanostores';
import { A as AccessControl, S as StatementsPrimitive, R as Role } from '../statement-CU-fdHXK.js';
import * as _better_fetch_fetch from '@better-fetch/fetch';
import { BetterFetchOption } from '@better-fetch/fetch';
import { o as organization, d as Organization, M as Member, I as Invitation, u as username } from '../index-D-u2S_Fl.js';
export { g as getPasskeyActions, c as passkeyClient, a as twoFactorClient } from '../index-D-u2S_Fl.js';
import { P as Prettify } from '../helper-C1ihmerM.js';
import '../index-C8A40nOX.js';
import 'arctic';
import 'zod';
import 'better-call';
import '../index-BMranMWG.js';
import 'kysely';
import '@simplewebauthn/types';

interface OrganizationClientOptions {
    ac: AccessControl;
    roles?: {
        [key in "admin" | "member" | "owner"]?: Role<any>;
    };
}
declare const organizationClient: <O extends OrganizationClientOptions>(options?: O) => {
    id: "organization";
    $InferServerPlugin: ReturnType<typeof organization>;
    getActions: ($fetch: _better_fetch_fetch.BetterFetch) => {
        $Infer: {
            ActiveOrganization: Prettify<Organization & {
                members: Prettify<Member & {
                    user: {
                        id: string;
                        name: string;
                        email: string;
                        image: string;
                    };
                }>[];
                invitations: Invitation[];
            }>;
            Organization: Organization;
            Invitation: Invitation;
            Member: Member;
        };
        organization: {
            setActive(orgId: string | null): void;
            hasPermission: (data: {
                permission: Partial<{ [key in keyof (O["ac"] extends AccessControl<infer S extends StatementsPrimitive> ? S extends Record<string, any[]> ? S & {
                    readonly organization: readonly ["update", "delete"];
                    readonly member: readonly ["create", "update", "delete"];
                    readonly invitation: readonly ["create", "cancel"];
                } : {
                    readonly organization: readonly ["update", "delete"];
                    readonly member: readonly ["create", "update", "delete"];
                    readonly invitation: readonly ["create", "cancel"];
                } : {
                    readonly organization: readonly ["update", "delete"];
                    readonly member: readonly ["create", "update", "delete"];
                    readonly invitation: readonly ["create", "cancel"];
                })]: (O["ac"] extends AccessControl<infer S extends StatementsPrimitive> ? S extends Record<string, any[]> ? S & {
                    readonly organization: readonly ["update", "delete"];
                    readonly member: readonly ["create", "update", "delete"];
                    readonly invitation: readonly ["create", "cancel"];
                } : {
                    readonly organization: readonly ["update", "delete"];
                    readonly member: readonly ["create", "update", "delete"];
                    readonly invitation: readonly ["create", "cancel"];
                } : {
                    readonly organization: readonly ["update", "delete"];
                    readonly member: readonly ["create", "update", "delete"];
                    readonly invitation: readonly ["create", "cancel"];
                })[key][number][]; }>;
                fetchOptions?: BetterFetchOption;
            }) => Promise<{
                data: null;
                error: {
                    message?: string | undefined;
                    status: number;
                    statusText: string;
                };
            } | {
                data: {
                    success: boolean;
                };
                error: null;
            }>;
        };
    };
    getAtoms: ($fetch: _better_fetch_fetch.BetterFetch) => {
        _listOrg: nanostores.PreinitializedWritableAtom<boolean>;
        _activeOrgSignal: nanostores.PreinitializedWritableAtom<boolean>;
        activeOrganization: nanostores.PreinitializedWritableAtom<{
            data: Prettify<{
                id: string;
                name: string;
                slug: string;
                createdAt: Date;
                logo?: string | undefined;
                metadata?: any;
            } & {
                members: (Member & {
                    user: {
                        id: string;
                        name: string;
                        email: string;
                        image: string;
                    };
                })[];
                invitations: Invitation[];
            }> | null;
            error: null | _better_fetch_fetch.BetterFetchError;
            isPending: boolean;
        }>;
        listOrganizations: nanostores.PreinitializedWritableAtom<{
            data: {
                id: string;
                name: string;
                slug: string;
                createdAt: Date;
                logo?: string | undefined;
                metadata?: any;
            }[] | null;
            error: null | _better_fetch_fetch.BetterFetchError;
            isPending: boolean;
        }>;
    };
    atomListeners: {
        matcher(path: string): boolean;
        signal: string;
    }[];
};

declare const usernameClient: () => {
    id: "username";
    $InferServerPlugin: ReturnType<typeof username>;
};

export { organizationClient, usernameClient };
