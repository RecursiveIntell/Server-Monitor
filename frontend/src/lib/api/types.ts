export type Settings = {
  server: {
    bind_host: string;
    bind_port: number;
  };
  paths: {
    cloudflared_config: string;
    fstab: string;
  };
  systemd: {
    cloudflared_unit: string;
    extra_units: string[];
  };
  security: {
    allow_actions: boolean;
    require_login: boolean;
  };
  checks: {
    default_interval_seconds: number;
    http_timeout_seconds: number;
    log_tail_lines: number;
  };
  llm: {
    enabled: boolean;
    provider: string;
    ollama: {
      base_url: string;
      model: string;
    };
    cloud: {
      enabled: boolean;
      provider: string;
    };
  };
};

export type SystemdService = {
  unit: string;
  load: string;
  active: string;
  sub: string;
  description: string;
};

export type PodmanContainer = Record<string, unknown>;

export type CloudflaredRoute = {
  hostname: string | null;
  service: string;
};

export type HealthResult = {
  ok: boolean;
  status_code: number | null;
  response_time_ms: number | null;
  error: string | null;
  checked_at?: string;
};

export type CloudflaredTarget = {
  hostname: string;
  service: string;
  url: string;
  last_result?: HealthResult;
};

export type LLMFailureExplanation = {
  summary: string;
  possible_causes: string[];
  suggested_actions: string[];
};

export type ChangeRecord = {
  id: number;
  path: string;
  diff: string;
  status: string;
  created_at: string;
  snapshot_id: number | null;
};
