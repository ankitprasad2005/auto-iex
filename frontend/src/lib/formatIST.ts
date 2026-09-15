// IEX is an Indian exchange, so every timestamp in this app is meaningful in
// IST regardless of which timezone the viewer's browser/OS happens to be
// set to. Date.prototype.toLocaleString() without an explicit timeZone
// silently uses the viewer's local zone instead, which is what produced
// wrong-looking times before this existed — always go through this helper
// instead of calling toLocaleString() directly on a timestamp.
export function formatIST(isoString: string): string {
  const formatted = new Date(isoString).toLocaleString("en-IN", {
    timeZone: "Asia/Kolkata",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });
  return `${formatted} IST`;
}
