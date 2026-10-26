import type { Metrics } from "@/data/types";

/** A partial read cannot erase a known field. This applies to normal refreshes; deletions clear their rows first. */
export function mergeMetricRead(current: Metrics, previous?: Metrics): Metrics {
  if (!previous) return current;
  return Object.fromEntries(Object.entries(current).map(([key, value]) => [key, value ?? previous[key as keyof Metrics]])) as Metrics;
}
