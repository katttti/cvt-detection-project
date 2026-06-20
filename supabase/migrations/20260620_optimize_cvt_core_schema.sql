create index if not exists idx_pressure_events_device_id
    on public.pressure_events (device_id);

create index if not exists idx_risk_assessments_pressure_event_id
    on public.risk_assessments (pressure_event_id);

create index if not exists idx_risk_assessments_transfer_event_id
    on public.risk_assessments (transfer_event_id);

create index if not exists idx_guardian_notifications_risk_assessment_id
    on public.guardian_notifications (risk_assessment_id);

drop policy if exists profiles_select_own on public.profiles;
drop policy if exists profiles_insert_own on public.profiles;
drop policy if exists profiles_update_own on public.profiles;
drop policy if exists guardian_links_select_related on public.guardian_links;
drop policy if exists guardian_links_insert_teen on public.guardian_links;
drop policy if exists guardian_links_update_related on public.guardian_links;
drop policy if exists devices_select_own on public.devices;
drop policy if exists devices_insert_own on public.devices;
drop policy if exists devices_update_own on public.devices;
drop policy if exists pressure_events_select_own on public.pressure_events;
drop policy if exists pressure_events_insert_own on public.pressure_events;
drop policy if exists transfer_events_select_own on public.transfer_events;
drop policy if exists transfer_events_insert_own on public.transfer_events;
drop policy if exists risk_assessments_select_own on public.risk_assessments;
drop policy if exists risk_assessments_insert_own on public.risk_assessments;
drop policy if exists guardian_notifications_select_related on public.guardian_notifications;
drop policy if exists guardian_notifications_insert_guardian_or_owner on public.guardian_notifications;

create policy profiles_select_own
    on public.profiles
    for select
    using ((select auth.uid()) = id);

create policy profiles_insert_own
    on public.profiles
    for insert
    with check ((select auth.uid()) = id);

create policy profiles_update_own
    on public.profiles
    for update
    using ((select auth.uid()) = id)
    with check ((select auth.uid()) = id);

create policy guardian_links_select_related
    on public.guardian_links
    for select
    using ((select auth.uid()) = teen_id or (select auth.uid()) = guardian_id);

create policy guardian_links_insert_teen
    on public.guardian_links
    for insert
    with check ((select auth.uid()) = teen_id);

create policy guardian_links_update_related
    on public.guardian_links
    for update
    using ((select auth.uid()) = teen_id or (select auth.uid()) = guardian_id)
    with check ((select auth.uid()) = teen_id or (select auth.uid()) = guardian_id);

create policy devices_select_own
    on public.devices
    for select
    using ((select auth.uid()) = profile_id);

create policy devices_insert_own
    on public.devices
    for insert
    with check ((select auth.uid()) = profile_id);

create policy devices_update_own
    on public.devices
    for update
    using ((select auth.uid()) = profile_id)
    with check ((select auth.uid()) = profile_id);

create policy pressure_events_select_own
    on public.pressure_events
    for select
    using ((select auth.uid()) = profile_id);

create policy pressure_events_insert_own
    on public.pressure_events
    for insert
    with check ((select auth.uid()) = profile_id);

create policy transfer_events_select_own
    on public.transfer_events
    for select
    using ((select auth.uid()) = profile_id);

create policy transfer_events_insert_own
    on public.transfer_events
    for insert
    with check ((select auth.uid()) = profile_id);

create policy risk_assessments_select_own
    on public.risk_assessments
    for select
    using ((select auth.uid()) = profile_id);

create policy risk_assessments_insert_own
    on public.risk_assessments
    for insert
    with check ((select auth.uid()) = profile_id);

create policy guardian_notifications_select_related
    on public.guardian_notifications
    for select
    using (
        (select auth.uid()) = guardian_id
        or exists (
            select 1
            from public.risk_assessments ra
            where ra.id = risk_assessment_id
              and ra.profile_id = (select auth.uid())
        )
    );

create policy guardian_notifications_insert_guardian_or_owner
    on public.guardian_notifications
    for insert
    with check (
        (select auth.uid()) = guardian_id
        or exists (
            select 1
            from public.risk_assessments ra
            where ra.id = risk_assessment_id
              and ra.profile_id = (select auth.uid())
        )
    );
