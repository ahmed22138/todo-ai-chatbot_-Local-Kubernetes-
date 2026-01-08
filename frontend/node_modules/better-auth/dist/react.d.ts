import * as _better_fetch_fetch from '@better-fetch/fetch';
import { B as BetterAuthPlugin, F as FieldAttribute, I as InferFieldOutput } from './index-BMranMWG.js';
import { U as UnionToIntersection, P as Prettify } from './helper-C1ihmerM.js';
import { ClientOptions, InferClientAPI, InferActions, BetterAuthClientPlugin, IsSignal } from './types.js';
import { useStore } from '@nanostores/react';
import 'kysely';
import './index-C8A40nOX.js';
import 'arctic';
import 'zod';
import 'better-call';
import 'nanostores';

type InferResolvedHooks<O extends ClientOptions> = O["plugins"] extends Array<infer Plugin> ? Plugin extends BetterAuthClientPlugin ? Plugin["getAtoms"] extends (fetch: any) => infer Atoms ? Atoms extends Record<string, any> ? {
    [key in keyof Atoms as IsSignal<key> extends true ? never : key extends string ? `use${Capitalize<key>}` : never]: () => ReturnType<Atoms[key]["get"]>;
} : {} : {} : {} : {};
declare function createAuthClient<Option extends ClientOptions>(options?: Option): UnionToIntersection<InferResolvedHooks<Option>> & InferClientAPI<Option> & InferActions<Option> & {
    useSession: (initialValue?: {
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
    } | null) => {
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
    };
    $Infer: {
        Session: {
            session: Prettify<UnionToIntersection<{
                id: string;
                userId: string;
                expiresAt: Date;
                ipAddress?: string | undefined;
                userAgent?: string | undefined;
            } & ((Option["plugins"] extends BetterAuthClientPlugin[] ? (Option["plugins"][number] extends infer T ? T extends BetterAuthClientPlugin ? T["$InferServerPlugin"] extends infer U ? U extends BetterAuthPlugin ? U : never : never : never : never)[] : never) extends (infer T_1)[] ? T_1 extends {
                schema: {
                    session: {
                        fields: infer Field;
                    };
                };
            } ? Field extends Record<string, FieldAttribute> ? { [key in keyof Field]: InferFieldOutput<Field[key]>; } : {} : {} : {})>>;
            user: Prettify<UnionToIntersection<{
                id: string;
                email: string;
                emailVerified: boolean;
                name: string;
                createdAt: Date;
                updatedAt: Date;
                image?: string | undefined;
            } & ((Option["plugins"] extends BetterAuthClientPlugin[] ? (Option["plugins"][number] extends infer T ? T extends BetterAuthClientPlugin ? T["$InferServerPlugin"] extends infer U ? U extends BetterAuthPlugin ? U : never : never : never : never)[] : never) extends (infer T_2)[] ? T_2 extends {
                schema: {
                    user: {
                        fields: infer Field_1;
                    };
                };
            } ? Field_1 extends Record<infer Key extends string | number | symbol, FieldAttribute> ? Prettify<{ [key_1 in Key as Field_1[key_1]["required"] extends false ? never : Field_1[key_1]["defaultValue"] extends string | number | boolean | Function | Date ? key_1 : never]: InferFieldOutput<Field_1[key_1]>; } & { [key_2 in Key as Field_1[key_2]["returned"] extends false ? never : key_2]?: InferFieldOutput<Field_1[key_2]> | undefined; }> : {} : {} : {})>>;
        };
    };
};
declare const useAuthQuery: typeof useStore;

export { createAuthClient, useAuthQuery };
