import { Primitive } from 'zod';

type LiteralString = "" | (string & Record<never, never>);
type Prettify<T> = Omit<T, never>;
type LiteralUnion<LiteralType, BaseType extends Primitive> = LiteralType | (BaseType & Record<never, never>);
type UnionToIntersection<U> = (U extends any ? (k: U) => void : never) extends (k: infer I) => void ? I : never;
type RequiredKeysOf<BaseType extends object> = Exclude<{
    [Key in keyof BaseType]: BaseType extends Record<Key, BaseType[Key]> ? Key : never;
}[keyof BaseType], undefined>;
type HasRequiredKeys<BaseType extends object> = RequiredKeysOf<BaseType> extends never ? false : true;
type WithoutEmpty<T> = T extends T ? ({} extends T ? never : T) : never;

export type { HasRequiredKeys as H, LiteralString as L, Prettify as P, RequiredKeysOf as R, UnionToIntersection as U, WithoutEmpty as W, LiteralUnion as a };
