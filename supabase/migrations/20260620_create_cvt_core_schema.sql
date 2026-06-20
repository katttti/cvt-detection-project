create extension if not exists pgcrypto;

create type public.profile_role as enum ('teen', 'guardian', 'admin');
create type public.guardian_link_status as enum ('pending', 'active', 'revoked');
create type public.risk_level as enum ('yellow', 'orange', 'red');
create type public.recommended_action as enum ('allow', 'warn', 'delay', 'notify_guardian');
create type public.notification_channel as enum ('push', 'sms', 'in_app');
create type public.delivery_status as enum ('queued', 'sent', 'failed', 'read');

create table if not exists public.profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    role public.profile_role not null,
    display_name text not null,
    phone text,
    created_at timestamptz not null default now()
);

create table if not exists public.guardian_links (
    id uuid primary key default gen_random_uuid(),
    teen_id uuid not null references public.profiles (id) on delete cascade,
    guardian_id uuid not null references public.profiles (id) on delete cascade,
    status public.guardian_link_status not null default 'pending',
    created_at timestamptz not null default now(),
    constraint guardian_links_no_self_link check (teen_id <> guardian_id),
    constraint guardian_links_unique_pair unique (teen_id, guardian_id)
);

create table if not exists public.devices (
    id uuid primary key default gen_random_uuid(),
    profile_id uuid not null references public.profiles (id) on delete cascade,
    device_label text,
    platform text not null,
    created_at timestamptz not null default now(),
    constraint devices_platform_check check (platform in ('ios', 'android'))
);

create table if not exists public.pressure_events (
    id uuid primary key default gen_random_uuid(),
    profile_id uuid not null references public.profiles (id) on delete cascade,
    device_id uuid not null references public.devices (id) on delete cascade,
    pressure_score numeric(5,4) not null,
    signal_summary jsonb not null default '{}'::jsonb,
    occurred_at timestamptz not null,
    created_at timestamptz not null default now(),
    constraint pressure_events_score_check check (pressure_score >= 0 and pressure_score <= 1)
);

create table if not exists public.transfer_events (
    id uuid primary key default gen_random_uuid(),
    profile_id uuid not null references public.profiles (id) on delete cascade,
    amount numeric(14,2) not null,
    recipient_hash text not null,
    is_new_recipient boolean not null default false,
    occurred_at timestamptz not null,
    created_at timestamptz not null default now(),
    constraint transfer_events_amount_check check (amount > 0)
);

create table if not exists public.risk_assessments (
    id uuid primary key default gen_random_uuid(),
    profile_id uuid not null references public.profiles (id) on delete cascade,
    pressure_event_id uuid not null references public.pressure_events (id) on delete cascade,
    transfer_event_id uuid not null references public.transfer_events (id) on delete cascade,
    risk_score numeric(5,4) not null,
    risk_level public.risk_level not null,
    reason_codes text[] not null default '{}',
    recommended_action public.recommended_action not null,
    created_at timestamptz not null default now(),
    constraint risk_assessments_score_check check (risk_score >= 0 and risk_score <= 1)
);

create table if not exists public.guardian_notifications (
    id uuid primary key default gen_random_uuid(),
    risk_assessment_id uuid not null references public.risk_assessments (id) on delete cascade,
    guardian_id uuid not null references public.profiles (id) on delete cascade,
    channel public.notification_channel not null,
    delivery_status public.delivery_status not null default 'queued',
    sent_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists idx_guardian_links_teen_id on public.guardian_links (teen_id);
create index if not exists idx_guardian_links_guardian_id on public.guardian_links (guardian_id);
create index if not exists idx_devices_profile_id on public.devices (profile_id);
create index if not exists idx_pressure_events_profile_id on public.pressure_events (profile_id);
create index if not exists idx_pressure_events_occurred_at on public.pressure_events (occurred_at desc);
create index if not exists idx_transfer_events_profile_id on public.transfer_events (profile_id);
create index if not exists idx_transfer_events_occurred_at on public.transfer_events (occurred_at desc);
create index if not exists idx_risk_assessments_profile_id on public.risk_assessments (profile_id);
create index if not exists idx_risk_assessments_created_at on public.risk_assessments (created_at desc);
create index if not exists idx_guardian_notifications_guardian_id on public.guardian_notifications (guardian_id);

alter table public.profiles enable row level security;
alter table public.guardian_links enable row level security;
alter table public.devices enable row level security;
alter table public.pressure_events enable row level security;
alter table public.transfer_events enable row level security;
alter table public.risk_assessments enable row level security;
alter table public.guardian_notifications enable row level security;

create policy profiles_select_own
    on public.profiles
    for select
    using (auth.uid() = id);

create policy profiles_insert_own
    on public.profiles
    for insert
    with check (auth.uid() = id);

create policy profiles_update_own
    on public.profiles
    for update
    using (auth.uid() = id)
    with check (auth.uid() = id);

create policy guardian_links_select_related
    on public.guardian_links
    for select
    using (auth.uid() = teen_id or auth.uid() = guardian_id);

create policy guardian_links_insert_teen
    on public.guardian_links
    for insert
    with check (auth.uid() = teen_id);

create policy guardian_links_update_related
    on public.guardian_links
    for update
    using (auth.uid() = teen_id or auth.uid() = guardian_id)
    with check (auth.uid() = teen_id or auth.uid() = guardian_id);

create policy devices_select_own
    on public.devices
    for select
    using (auth.uid() = profile_id);

create policy devices_insert_own
    on public.devices
    for insert
    with check (auth.uid() = profile_id);

create policy devices_update_own
    on public.devices
    for update
    using (auth.uid() = profile_id)
    with check (auth.uid() = profile_id);

create policy pressure_events_select_own
    on public.pressure_events
    for select
    using (auth.uid() = profile_id);

create policy pressure_events_insert_own
    on public.pressure_events
    for insert
    with check (auth.uid() = profile_id);

create policy transfer_events_select_own
    on public.transfer_events
    for select
    using (auth.uid() = profile_id);

create policy transfer_events_insert_own
    on public.transfer_events
    for insert
    with check (auth.uid() = profile_id);

create policy risk_assessments_select_own
    on public.risk_assessments
    for select
    using (auth.uid() = profile_id);

create policy risk_assessments_insert_own
    on public.risk_assessments
    for insert
    with check (auth.uid() = profile_id);

create policy guardian_notifications_select_related
    on public.guardian_notifications
    for select
    using (
        auth.uid() = guardian_id
        or exists (
            select 1
            from public.risk_assessments ra
            where ra.id = risk_assessment_id
              and ra.profile_id = auth.uid()
        )
    );

create policy guardian_notifications_insert_guardian_or_owner
    on public.guardian_notifications
    for insert
    with check (
        auth.uid() = guardian_id
        or exists (
            select 1
            from public.risk_assessments ra
            where ra.id = risk_assessment_id
              and ra.profile_id = auth.uid()
        )
    );
