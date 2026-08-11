# Estate Project — Context Summary

Django REST Framework backend with three core apps: `accounts`, `agencies`, `property`.

## accounts

Custom user model + phone/OTP based auth.

**Model** (`accounts/models.py`)
- `User(AbstractBaseUser, PermissionsMixin)` — `phone_number` (unique, USERNAME_FIELD), `email` (unique), `first_name`, `last_name`, `role` (`AGENT` / `CUSTOMER` / `ADMIN`, default `CUSTOMER`), `is_active`, `is_staff`, `date_joined`.
- `UserManager` (`accounts/managers.py`) — `create_user` requires phone/email/first/last name; `create_superuser` forces `is_staff`, `is_superuser`, `role=ADMIN`.

**OTP infra**
- `accounts/otp.py` — helpers: `generate_otp_code` (5-digit), `generate_session_token` (uuid4), cache key builders (`otp_data_key`, `otp_limit_key`, `otp_session_key`). `OTP_TTL_SECONDS=120`, `OTP_RATE_LIMIT_SECONDS=5`.
- `accounts/services/otp_service.py` — `OTPService.send_otp` (generates code, stores in cache, rate-limits, returns session token) and `verify_otp` (checks code, max 10 attempts, deletes on success/lockout).
- `accounts/utils.py` — `send_otp_code` sends via Kavenegar SMS API (currently commented out; just prints the code — dev/stub mode).
- `accounts/services/auth_service.py` — `AuthService.complete_registration` (creates user from cached phone + submitted info, issues JWT pair) and `reset_password` (sets new password from cached reset token).

**Views/flows** (`accounts/views.py`, all DRF `APIView`, JWT via `rest_framework_simplejwt`)
- Register: send OTP → verify OTP (returns registration token) → complete registration (creates user, returns access/refresh tokens).
- Login: send OTP (requires correct password first) → verify OTP (returns access/refresh tokens).
- `UserSendInfoView` / `UserUpdateInfoView` — get/patch own profile (auth required).
- Password reset: 3-step (send OTP → verify OTP → set new password via reset token).
- Change phone number: 2-step OTP flow, old phone stashed in `request.session`.
- Account deletion: 2-step OTP flow, deletes user on verification.

**URLs** (`accounts/urls.py`, prefix likely `accounts/`, app_name `accounts`) — all under `user/...` (register, login, info, reset password steps 1-3, change phone steps 1-2, delete steps 1-2).

**Admin** — custom `UserAdmin` with custom `UserCreationForm`/`UserChangeForm` (password confirm on create).

## agencies

Real-estate agency profiles, one per agent user.

**Model** (`agencies/models.py`)
- `Agency` — `agent` (OneToOne → User), `name`, `license_number`, `business_phone`, `description`, `province`, `city`, `exact_address`, `is_verified` (default False), `created`, `updated`.

**Permissions** (`agencies/permissions.py`)
- `IsAgent` — allows only authenticated users with `role == AGENT`.

**Views** (`agencies/views.py`)
- `CreateAgencyView` — agent-only, one agency per agent (400 if exists).
- `UpdateAgencyView` — agent-only, patches own agency.
- `ListAgencyView` — public, lists only `is_verified=True` agencies.
- `DetailPublicAgencyView` — public, by pk, only if verified.
- `DetailPrivetAgencyView` — agent-only, own agency detail (verified or not).
- `DeleteAgencyView` — agent-only, deletes own agency.

**Serializers** — `AgencySerializer` (create/update fields), `AgencyListSerializer` (pk/name/province/city), `AgencyDetailSerializer` (all fields).

**URLs** (`agencies/urls.py`, app_name `agencies`) — `create/`, `update/`, `list/`, `detail/public/<pk>/`, `detail/privet/`, `delete/`.

**Admin** — list/search/filter by name, license_number, business_phone, agent phone; ordered by `-created`.

## property

Listings owned by an agency, with images.

**Models** (`property/models.py`)
- `Property` — FK to `Agency` (`properties` related_name), `title`, unique `slug` (auto-generated from title+city on save, deduped with counter suffix), `description`, `listing_type` (SALE/RENT), `property_type` (APARTMENT/HOUSE/VILLA/LAND/OFFICE/SHOP/WAREHOUSE), `status` (ACTIVE/INACTIVE/SOLD/RENTED/PENDING, default ACTIVE), `price`, `area`, `bedrooms`, `bathrooms`, `has_parking`, `floor`, `total_floors`, `year_built`, `province`, `city`, `address`, `latitude`/`longitude`, `is_featured`, `view_count`, `created`/`updated`. Ordered by `-created`; several indexed fields.
- `PropertyImage` — FK to `Property` (`images` related_name), `image`, `is_first`, `created`.

**Views** (`property/views.py`)
- `CreatePropertyView` — agent-only; requires the agent to have an agency; accepts up to 3 images (image1 required, image2/3 optional) via `CreatePropertySerializer`.
- `ListPropertyView` — public; excludes `INACTIVE` listings.
- `PropertyDetailView` — public; looked up by slug; increments `view_count` atomically via `F()` on each view.
- `UpdatePropertyView` — agent-only; can only patch a property belonging to their own agency (looked up by slug + agency).
- `DeletePropertyView` — agent-only; same ownership scoping as update.

**Serializers**
- `CreatePropertySerializer` — writable fields + `image1/2/3`; creates `Property` and associated `PropertyImage` rows atomically (`image1` marked `is_first=True`).
- `ListPropertySerializer` — summary fields + nested images.
- `PropertyDetailSerializer` — full fields + nested `agency` (via `AgencyListSerializer`) + images.
- `PropertyUpdateSerializer` — same writable fields as create, minus images.

**URLs** (`property/urls.py`, app_name `property`) — `create/`, `list/`, `detail/<slug>/`, `update/<slug>/`, `delete/<slug>/`.

**Admin** — `PropertyAdmin` with inline `PropertyImage` editing.

## Cross-app relationships

`User (accounts)` —1:1→ `Agency (agencies)` —1:N→ `Property (property)` —1:N→ `PropertyImage`.

Ownership/access pattern is consistent across `agencies` and `property`: agent-only mutation endpoints scoped to the requesting user's own agency, with public read-only endpoints filtered to verified/active records.