import type { ReactNode } from "react";
import type { Anchor, AnchorStatus, AnchorVerifyResult } from "../api/types";
import { formatIST } from "../lib/formatIST";

const SHORT_HASH_LENGTH = 10;

export function shortHash(hash: string): string {
  return hash.length > SHORT_HASH_LENGTH ? `${hash.slice(0, SHORT_HASH_LENGTH)}…` : hash;
}

interface Props {
  status: AnchorStatus | null;
  anchors: Anchor[];
  onAnchorNow: () => void;
  anchoring: boolean;
  onVerify: (id: number) => void;
  verifyResults: Record<number, AnchorVerifyResult | string>;
  message: string | null;
}

const LABEL = "font-mono text-[11px] uppercase tracking-label text-nd-text-secondary";

function StatusField({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1 min-w-0">
      <span className={LABEL}>{label}</span>
      {children}
    </div>
  );
}

function StatusCard({ status }: { status: AnchorStatus | null }) {
  if (status === null) {
    return <p className="font-mono text-sm text-nd-text-secondary">Loading anchoring status…</p>;
  }
  return (
    <div className="flex flex-col gap-4 border border-nd-border p-4">
      <div className="flex flex-wrap gap-x-12 gap-y-4">
        <StatusField label="Network">
          <span className="font-display text-2xl text-nd-text-display">{status.network}</span>
        </StatusField>
        <StatusField label="Chain id">
          <span className="font-display text-2xl text-nd-text-display">{status.chain_id}</span>
        </StatusField>
        <StatusField label="Anchoring">
          <span
            className={`font-display text-2xl ${status.enabled ? "text-nd-text-display" : "text-nd-accent"}`}
          >
            {status.enabled ? "Enabled" : "Disabled"}
          </span>
        </StatusField>
      </div>
      <StatusField label="Wallet address">
        <span className="font-mono text-xs text-nd-text-primary break-all">{status.wallet_address ?? "—"}</span>
      </StatusField>
      {!status.enabled && (
        <p className="font-mono text-xs text-nd-text-secondary max-w-xl">
          Anchoring is disabled because ANCHOR_PRIVATE_KEY is not set on the backend. Set it to a funded
          Polygon Amoy testnet wallet key and restart the backend to publish chain heads.
        </p>
      )}
    </div>
  );
}

function VerifyResult({ result }: { result: AnchorVerifyResult | string | undefined }) {
  if (result === undefined) return null;
  if (typeof result === "string") {
    return <span className="font-mono text-[11px] text-nd-accent">{result}</span>;
  }
  if (result.valid) {
    return <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-primary">VALID</span>;
  }
  return (
    <div className="flex flex-col gap-1 text-nd-accent">
      <span className="font-mono text-[11px] uppercase tracking-label">TAMPERED</span>
      {result.mismatches.length > 0 && (
        <ul className="font-mono text-[11px] list-disc pl-4">
          {result.mismatches.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function HashCell({ hash }: { hash: string }) {
  return (
    <td className="py-1.5 pr-4 whitespace-nowrap">
      <span title={hash}>{shortHash(hash)}</span>
    </td>
  );
}

export function AnchorsView({ status, anchors, onAnchorNow, anchoring, onVerify, verifyResults, message }: Props) {
  const canAnchor = status !== null && status.enabled && !anchoring;

  return (
    <div className="flex flex-col gap-8">
      <StatusCard status={status} />

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-4">
          <p className="font-mono text-xs text-nd-text-secondary max-w-md">
            Each anchor publishes the heads of the scrape, settlement and price ledger chains to the public
            testnet, so anyone can check the local ledgers have not been rewritten since.
          </p>
          <button
            type="button"
            onClick={onAnchorNow}
            disabled={!canAnchor}
            className="font-mono text-[11px] uppercase tracking-label px-3 py-1.5 border border-nd-border-visible text-nd-text-primary hover:border-nd-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
          >
            {anchoring ? "Anchoring…" : "Anchor now"}
          </button>
        </div>
        {message && (
          <p role="status" className="font-mono text-xs text-nd-text-primary">
            {message}
          </p>
        )}
      </div>

      {anchors.length === 0 ? (
        <p className="font-mono text-sm text-nd-text-secondary">No anchors yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[880px] font-mono text-xs text-nd-text-primary border-collapse">
            <thead>
              <tr className="text-left text-nd-text-secondary uppercase tracking-label text-[11px]">
                <th className="py-2 pr-4">Time</th>
                <th className="py-2 pr-4">Scrape</th>
                <th className="py-2 pr-4">Settlement</th>
                <th className="py-2 pr-4">Price</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Tx</th>
                <th className="py-2 pr-4">Verify</th>
              </tr>
            </thead>
            <tbody>
              {anchors.map((a) => (
                <tr key={a.id} className="border-t border-nd-border align-top">
                  <td className="py-1.5 pr-4 whitespace-nowrap">{formatIST(a.created_at)}</td>
                  <HashCell hash={a.scrape_head_hash} />
                  <HashCell hash={a.settlement_head_hash} />
                  <HashCell hash={a.price_ledger_head_hash} />
                  <td className="py-1.5 pr-4">
                    {a.status === "confirmed" ? (
                      <span>confirmed</span>
                    ) : (
                      <div className="flex flex-col gap-1 text-nd-accent">
                        <span title={a.error ?? undefined}>failed</span>
                        {a.error && <span className="text-[11px] max-w-[16rem] break-words">{a.error}</span>}
                      </div>
                    )}
                  </td>
                  <td className="py-1.5 pr-4 whitespace-nowrap">
                    {a.tx_hash === null ? (
                      "—"
                    ) : a.explorer_url ? (
                      <a
                        href={a.explorer_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        title={a.tx_hash}
                        className="underline decoration-nd-border-visible hover:text-nd-accent"
                      >
                        {shortHash(a.tx_hash)}
                      </a>
                    ) : (
                      <span title={a.tx_hash}>{shortHash(a.tx_hash)}</span>
                    )}
                  </td>
                  <td className="py-1.5 pr-4">
                    {a.status === "confirmed" && a.tx_hash !== null && (
                      <div className="flex flex-col items-start gap-1">
                        <button
                          type="button"
                          onClick={() => onVerify(a.id)}
                          className="font-mono text-[11px] uppercase tracking-label px-2 py-1 border border-nd-border-visible text-nd-text-primary hover:border-nd-accent transition-colors"
                        >
                          Verify
                        </button>
                        <VerifyResult result={verifyResults[a.id]} />
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
