import type { Session, SupabaseClient, User } from "@supabase/supabase-js";
import { writable } from "svelte/store";

// only to be used in components to avoid prop drilling
export const SupaStore = writable<SupabaseClient>();
export const UserStore = writable<User | null>();
export const SessionStore = writable<Session | null>();