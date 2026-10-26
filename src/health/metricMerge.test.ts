import { describe, expect, it } from "vitest";
import { emptyMetrics } from "@/data/types";
import { mergeMetricRead } from "./metricMerge";

describe("partial daily metric refresh", () => {
  const previous = { ...emptyMetrics("2026-10-27"), hrvMs: 54, rhrBpm: 58, calories: 1200, steps: 500 };
  it("retains missing fields while accepting new measurements", () => {
    expect(mergeMetricRead({ ...emptyMetrics(previous.day), steps: 750 }, previous)).toMatchObject({ hrvMs: 54, rhrBpm: 58, calories: 1200, steps: 750 });
  });
  it("accepts zero and downward corrections rather than taking field maxima", () => {
    expect(mergeMetricRead({ ...emptyMetrics(previous.day), calories: 0, steps: 400, hrvMs: 45 }, previous)).toMatchObject({ calories: 0, steps: 400, hrvMs: 45 });
  });
});
