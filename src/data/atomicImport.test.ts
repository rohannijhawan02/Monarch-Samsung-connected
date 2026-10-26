// Exercise the actual Store SQL against SQLite, with only the Expo transport adapted for Node.
import { afterEach, describe, expect, it, vi } from "vitest";
import type { SQLInputValue } from "node:sqlite";
import { emptyMetrics } from "./types";

const connections = vi.hoisted(() => [] as { close(): void }[]);
vi.mock("expo-sqlite", async () => {
  const { DatabaseSync } = await import("node:sqlite");
  return {
    deleteDatabaseAsync: async () => {},
    openDatabaseAsync: async () => {
      const db = new DatabaseSync(":memory:");
      connections.push(db);
      const adapter = {
        isInTransactionSync: () => false,
        execAsync: async (sql: string) => { db.exec(sql); },
        runAsync: async (sql: string, params: SQLInputValue[] = []) => db.prepare(sql).run(...params),
        getFirstAsync: async (sql: string, params: SQLInputValue[] = []) => db.prepare(sql).get(...params) ?? null,
        getAllAsync: async (sql: string, params: SQLInputValue[] = []) => db.prepare(sql).all(...params),
        prepareAsync: async (sql: string) => {
          const statement = db.prepare(sql);
          return { executeAsync: async (params: SQLInputValue[]) => statement.run(...params), finalizeAsync: async () => {} };
        },
        withExclusiveTransactionAsync: async (task: (transaction: unknown) => Promise<void>) => {
          db.exec("begin immediate");
          try { await task(adapter); db.exec("commit"); }
          catch (error) { db.exec("rollback"); throw error; }
        },
        closeAsync: async () => {},
      };
      return adapter;
    },
  };
});

const { openStore } = await import("./db");
afterEach(() => { for (const db of connections.splice(0)) db.close(); });

describe("SQLite atomic import", () => {
  it("rolls back clearing and partially written samples when an import fails", async () => {
    const store = await openStore("atomic-import-test");
    const metric = { ...emptyMetrics("2026-10-27"), hrvMs: 55, steps: 500 };
    await store.upsertMetrics([metric]);
    await store.putHr([{ ts: 100, bpm: 60 }]);
    await expect(store.atomicImport(async (transaction) => {
      await transaction.clearImported({ from: metric.day, to: metric.day }, 0, 1000, { keepScores: true });
      await transaction.putHr([{ ts: 200, bpm: 90 }]);
      await transaction.upsertMetrics([{ ...metric, steps: 700 }]);
      throw new Error("sensor read failed");
    })).rejects.toThrow("sensor read failed");
    expect(await store.allMetrics()).toEqual([metric]);
    expect(await store.readHr(0, 1000)).toEqual([{ ts: 100, bpm: 60 }]);
  });

  it("commits multiple Store writes without starting nested SQLite transactions", async () => {
    const store = await openStore("atomic-import-test");
    await store.atomicImport(async (transaction) => {
      await transaction.upsertMetrics([{ ...emptyMetrics("2026-10-27"), steps: 750 }]);
      await transaction.putHr([{ ts: 100, bpm: 65 }]);
      await transaction.setSyncState({ lastSyncTs: 200 });
    });
    expect((await store.allMetrics())[0].steps).toBe(750);
    expect(await store.readHr(0, 1000)).toEqual([{ ts: 100, bpm: 65 }]);
    expect((await store.getSyncState()).lastSyncTs).toBe(200);
  });
});
