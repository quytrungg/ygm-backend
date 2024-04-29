# Changelog of `ygm` project

### 1.0.0

- Implement logic to generate weeks for rally session page

Task: [YGMP1-459](https://saritasa.atlassian.net/browse/YGMP1-459)

### 0.95.0

- Add rally session list API.

Task: [YGMP1-422](https://saritasa.atlassian.net/browse/YGMP1-422)

### 0.94.0

- Update API to allow StoredMember to have multiple contacts.

Task: [YGMP1-375](https://saritasa.atlassian.net/browse/YGMP1-375)

### 0.93.0

- Disallow CA and chair to sell contracts.

Task: [YGMP1-384](https://saritasa.atlassian.net/browse/YGMP1-384)

### 0.92.0

- Add `UserCampaign` delete API: allow deleting users who have no contracts.

Task: [YGMP1-380](https://saritasa.atlassian.net/browse/YGMP1-380)

### 0.91.0

- Update leaderboard stats calculation: calculate week revenue based on contracts' approval time instead of creation time

Task: [YGMP1-287](https://saritasa.atlassian.net/browse/YGMP1-287)

### 0.90.0

- Update contract approve API: allow CA to select levels for approval

Task: [YGMP1-392](https://saritasa.atlassian.net/browse/YGMP1-392)

### 0.89.0

- Update subdomain existence check API: always return chamber data

Task: [YGMP1-364](https://saritasa.atlassian.net/browse/YGMP1-364)

### 0.88.0

- Actualize `product_name` field for contract detail CA API.

Task: [YGMP1-390](https://saritasa.atlassian.net/browse/YGMP1-390)

### 0.87.0

- Provide leaderboard APIs for CA site

Task: [YGMP1-151](https://saritasa.atlassian.net/browse/YGMP1-151)

### 0.86.0

- Add ability to view data by campaign

Task: [YGMP1-376](https://saritasa.atlassian.net/browse/YGMP1-376)

### 0.85.0

- Update permissions for level instance APIs.

Task: [YGMP1-391](https://saritasa.atlassian.net/browse/YGMP1-391)

### 0.84.0

- Update api for declined renewal contract

Task: [YGMP1-386](https://saritasa.atlassian.net/browse/YGMP1-386)

### 0.83.0

- Update subdomain check API: return the latest campaign info
- Update public base viewset: use the latest campaign info

Task: [YGMP1-364](https://saritasa.atlassian.net/browse/YGMP1-364)

### 0.82.0

- Update contract list API for CA site: exclude contracts of previous campaigns

Task: [YGMP1-367](https://saritasa.atlassian.net/browse/YGMP1-367)

### 0.81.0

- Update contract list API for CA site: exclude approved contracts of previous campaigns

Task: [YGMP1-367](https://saritasa.atlassian.net/browse/YGMP1-367)

### 0.80.0

- Update `draft` contracts' cost if levels' cost change

Task: [YGMP1-366](https://saritasa.atlassian.net/browse/YGMP1-366)

### 0.79.0

- Fix issue with `portion` field precision
  - increase decimal digits to store values with high precision, which result in more accurate stats calculation

Task: [YGMP1-346](https://saritasa.atlassian.net/browse/YGMP1-346)

### 0.78.0

- Filter out sold-out levels in remaining sponsorship API.

Task: [YGMP1-347](https://saritasa.atlassian.net/browse/YGMP1-347)

### 0.77.0

- allow SA to view chamber's `finished` campaigns' data.

Task: [YGMP1-350](https://saritasa.atlassian.net/browse/YGMP1-350)

### 0.76.0

- allow user creation/edit
- allow team creation/edit
- allow inventory edit

Task: [YGMP1-355](https://saritasa.atlassian.net/browse/YGMP1-355)

### 0.75.0

- Change unique constraint on `User`'s email to conditional unique constraint
  - Avoid error when user is deleted and chamber use deleted email to invite volunteer

Task: [YGMP1-354](https://saritasa.atlassian.net/browse/YGMP1-354)

### 0.74.0

- Add missing filter in UserCampaign list VS API to support FE

Task: [YGMP1-313](https://saritasa.atlassian.net/browse/YGMP1-313)

### 0.73.0

- Update team list API response
  - Add `is_active` field for each member

Task: [YGMP1-271](https://saritasa.atlassian.net/browse/YGMP1-271)

### 0.72.0

- Send email notification to chamber admins when there's new contract needing review.

Task: [YGMP1-339](https://saritasa.atlassian.net/browse/YGMP1-339)

### 0.71.0

- Return `member_name` to display in User table instead of `company_name`.

Task: [YGMP1-271](https://saritasa.atlassian.net/browse/YGMP1-271)

### 0.70.0

- Allow actions on public contracts when campaign is in `renewal` status.

Task: [YGMP1-333](https://saritasa.atlassian.net/browse/YGMP1-333)

### 0.69.0

- Require CA to fill chamber logo in branding update API

Task: [YGMP1-335](https://saritasa.atlassian.net/browse/YGMP1-335)

### 0.68.0

- Update user campaign edit API:
  - Allow CA to set user's member

Task: [YGMP1-271](https://saritasa.atlassian.net/browse/YGMP1-271)

### 0.67.0

- Add `is_renewed` flag for `Contract`.
- Add `is_renewed` filter for contract APIs.
- Update permission to edit contract in VS.

Task: [YGMP1-333](https://saritasa.atlassian.net/browse/YGMP1-333)

### 0.66.0

- Add default ordering to prevent notes from changing order on FE after update.

Task: [YGMP1-181](https://saritasa.atlassian.net/browse/YGMP1-181)

### 0.65.0

- Filter notes of current campaign in note list API.

Task: [YGMP1-181](https://saritasa.atlassian.net/browse/YGMP1-181)

### 0.64.0

- Update contract list and detail API for CA site.

Task: [YGMP1-312](https://saritasa.atlassian.net/browse/YGMP1-312)

### 0.63.0

- Provide API to duplicate product.

Task: [YGMP1-224](https://saritasa.atlassian.net/browse/YGMP1-224)

### 0.62.0

- Provide API to duplicate product category.

Task: [YGMP1-205](https://saritasa.atlassian.net/browse/YGMP1-205)

### 0.61.0

- Support external url for product's attachment.

Task: [YGMP1-217](https://saritasa.atlassian.net/browse/YGMP1-217)

### 0.60.0

- Add contract delete VS API.

Task: [YGMP1-216](https://saritasa.atlassian.net/browse/YGMP1-216)

### 0.59.0

- Update public contract info API, provide public contract sign API.

Task: [YGMP1-244](https://saritasa.atlassian.net/browse/YGMP1-244)

### 0.58.0

- Provide landing page information API.

Task: [YGMP1-249](https://saritasa.atlassian.net/browse/YGMP1-249)

### 0.57.0

- Provide contract list/create/update APIs for VS.

Task: [YGMP1-166](https://saritasa.atlassian.net/browse/YGMP1-166)

### 0.56.0

- Create/update chamber admin from chamber's CEO information.

Task: [YGMP1-187](https://saritasa.atlassian.net/browse/YGMP1-187)

### 0.55.0

- No longer require campaign to be live for volunteer to access VS.

Task: [YGMP1-194](https://saritasa.atlassian.net/browse/YGMP1-194)

### 0.54.0

- Provide purchasing member APIs.

Task: [YGMP1-162](https://saritasa.atlassian.net/browse/YGMP1-162)

### 0.53.1

- Add `team` information to profile volunteer API.

Task: [YGMP1-168](https://saritasa.atlassian.net/browse/YGMP1-168)

### 0.53.0

- Provide incentive records reorder API.

Task: [YGMP1-240](https://saritasa.atlassian.net/browse/YGMP1-240)

### 0.52.0

- Provide inventory records reorder API.

Task: [YGMP1-236](https://saritasa.atlassian.net/browse/YGMP1-236)

### 0.51.0

- Provide timeline records reorder API.

Task: [YGMP1-232](https://saritasa.atlassian.net/browse/YGMP1-232)

### 0.50.1

- Disallow `blank` for `UserCampaign`'s `first_name` and `last_name`.

Task: [YGMP1-194](https://saritasa.atlassian.net/browse/YGMP1-194)

### 0.50.0

- Provide API for volunteer signup flow.

Task: [YGMP1-194](https://saritasa.atlassian.net/browse/YGMP1-194)

### 0.49.0

- Provide API to check if a subdomain belongs to any chamber.

Task: [YGMP1-193](https://saritasa.atlassian.net/browse/YGMP1-193)

### 0.48.3

- Remove `UserAttributeSimilarityValidator` and `CommonPasswordValidator`.

Task: [YGMP1-186](https://saritasa.atlassian.net/browse/YGMP1-186)

### 0.48.2

- Update campaign validation:
  - No campaigns of the same chamber have same name.
  - Only one campaign per chamber per year.
  - Only one ongoing campaign per chamber.

Task: [YGMP1-225](https://saritasa.atlassian.net/browse/YGMP1-225)

### 0.48.1

- Update permission for contract delete API.
- Contract list API for CA site now returns all contracts of user's chamber.
- Fix filtering condition for contract list API for VS site.

Task: [YGMP1-217](https://saritasa.atlassian.net/browse/YGMP1-217)

### 0.48.0

- Add `is_renewed` field in Campaign models, update admin UI and serializers.

Task: [YGMP1-221](https://saritasa.atlassian.net/browse/YGMP1-221)

### 0.47.0

- Provide product category's update name API.

Task: [YGMP1-204](https://saritasa.atlassian.net/browse/YGMP1-204)

### 0.46.0

- Provide campaign's inventory statistics API.

Task: [YGMP1-210](https://saritasa.atlassian.net/browse/YGMP1-210)

### 0.45.0

- Update permissions for contract APIs.

Task: [YGMP1-217](https://saritasa.atlassian.net/browse/YGMP1-217)

### 0.44.0

- Implement chamber product category statistics API.

Task: [YGMP1-210](https://saritasa.atlassian.net/browse/YGMP1-210)

### 0.43.0

- Provide volunteer login API.

Task: [YGMP1-193](https://saritasa.atlassian.net/browse/YGMP1-193)

### 0.42.0

- Update volunteer profile API, add max length constraint for `home_state` field, add validator for `birthday` field.

Task: [YGMP1-168](https://saritasa.atlassian.net/browse/YGMP1-168)

### 0.41.0

- Add note field in contract list API.

Task: [YGMP1-195](https://saritasa.atlassian.net/browse/YGMP1-195)

### 0.40.0

- Provide API for marketing opportunities page.

Task: [YGMP1-191](https://saritasa.atlassian.net/browse/YGMP1-191)

### 0.39.0

- Add restriction: Each chamber can only have 1 campaign in `open` or `live` status at a time.

Task: [YGMP1-180](https://saritasa.atlassian.net/browse/YGMP1-180)

# 0.38.1
- Add `pre_trc_income` field to `Campaign` APIs.

Task: [YGMP1-145](https://saritasa.atlassian.net/browse/YGMP1-145)

### 0.38.0

- Improve campaign update API.

Task: [YGMP1-145](https://saritasa.atlassian.net/browse/YGMP1-145)

### 0.37.0

- Provide profile API for volunteers.

Task: [YGMP1-168](https://saritasa.atlassian.net/browse/YGMP1-168)

### 0.36.0

- Provide invoice list API.

Task: [YGMP1-154](https://saritasa.atlassian.net/browse/YGMP1-154)

### 0.35.0

- Provide Resource CRUD.
- Add `/api/v1/admin/resource` endpoints.
- Update Resource Model with `user_group` and `file_type` fields.

Task: [YGMP1-86](https://saritasa.atlassian.net/browse/YGMP1-86)

### 0.34.0

- Add api for stored members.

Task: [YGMP1-142](https://saritasa.atlassian.net/browse/YGMP1-142)

### 0.33.0

- Improve the `product_category` methods.

Task: [YGMP1-138](https://saritasa.atlassian.net/browse/YGMP1-138)

### 0.32.0

- Provide APIs for sale report page.

Task: [YGMP1-131](https://saritasa.atlassian.net/browse/YGMP1-131)

### 0.31.0

- Fix issue with custom middleware, which relies on session middleware to work.

Task: [YGMP1-111](https://saritasa.atlassian.net/browse/YGMP1-111)

### 0.30.2

- Fix invite user API permissions.

Task: [YGMP1-112](https://saritasa.atlassian.net/browse/YGMP1-112)

### 0.30.1

- Fix actions to assign team error.

Task: [YGMP1-116](https://saritasa.atlassian.net/browse/YGMP1-116)

### 0.30.0

- Provide contract approve/decline APIs.

Task: [YGMP1-122](https://saritasa.atlassian.net/browse/YGMP1-122)

### 0.29.0

- Reorganize Campaign APIs.

Task: [YGMP1-126](https://saritasa.atlassian.net/browse/YGMP1-126)

### 0.28.0

- Provide decline product API.

Task: [YGMP1-124](https://saritasa.atlassian.net/browse/YGMP1-124)

### 0.27.0

- Provide API for getting public information of a contract.

Task: [YGMP1-123](https://saritasa.atlassian.net/browse/YGMP1-123)

### 0.26.0

- Provide Contract list API.

Task: [YGMP1-120](https://saritasa.atlassian.net/browse/YGMP1-120)

### 0.25.0

- Provide models, admin UIs, factories for Incentive app.
- Provide CRUD APIs for Incentive.
- Provide APIs for getting available Incentive Qualifier names and amounts.

Task: [YGMP1-113](https://saritasa.atlassian.net/browse/YGMP1-113)

### 0.24.0

- Provide actions to assign volunteers in campaign.

Task: [YGMP1-116](https://saritasa.atlassian.net/browse/YGMP1-116)

### 0.23.0

- Add profile update API for Chamber Admins.

Task: [YGMP1-115](https://saritasa.atlassian.net/browse/YGMP1-115)

### 0.22.0

- Add user create API for chamber admin.

Task: [YGMP1-112](https://saritasa.atlassian.net/browse/YGMP1-112)

### 0.21.0

- Update `mail_address` field in `Chamber` model.
- Change `mail_address` in `Chamber` detail and list API to `trc_coord_email`.

Task: [YGMP1-75](https://saritasa.atlassian.net/browse/YGMP1-75)

### 0.20.0

- Provide campaign CRUD API endpoints for Super Admins and Chamber Admins.

Task: [YGMP1-94](https://saritasa.atlassian.net/browse/YGMP1-94)

### 0.19.1

- Add fields to `User` model.
- Extend the profile API.

Task: [YGMP1-110](https://saritasa.atlassian.net/browse/YGMP1-110)

### 0.19.0

- Add profile update API for Super Admin.

Task: [YGMP1-109](https://saritasa.atlassian.net/browse/YGMP1-109)

Task: [YGMP1-110](https://saritasa.atlassian.net/browse/YGMP1-110)

### 0.18.0

- Add chamber update API for chamber admin.

Task: [YGMP1-93](https://saritasa.atlassian.net/browse/YGMP1-93)

### 0.17.0

- Provide Team management CRUD APIs.

Task: [YGMP1-111](https://saritasa.atlassian.net/browse/YGMP1-111)

### 0.16.0

- Add inventory APIs for chamber admin.
  * Add `ProductCategory` CRUD APIs.
  * Add `Product` CRUD APIs.
  * Add `Level` CRUD APIs.

Task: [YGMP1-103](https://saritasa.atlassian.net/browse/YGMP1-103)

### 0.15.0

- Provide models for Timeline app.
- Provide Timeline CRUD.

Task: [YGMP1-104](https://saritasa.atlassian.net/browse/YGMP1-104)

### 0.14.2

- Switch to `OneToOneField` for `ChamberBranding` model.
- Update `Chamber` CRUD APIs.

Task: [YGMP1-75](https://saritasa.atlassian.net/browse/YGMP1-75)

### 0.14.1

- Fix chamber detail/update API for super admin.
  * fix `chamber_logo` field not included in response.

- Apply convention for naming serializer/viewset and doc versioning.

Task: [YGMP1-75](https://saritasa.atlassian.net/browse/YGMP1-75)

### 0.14.0

- Add account register API for chamber admin.
- Add account registration info retrieval API.

Task: [YGMP1-90](https://saritasa.atlassian.net/browse/YGMP1-90)

### 0.13.0

- Add Chamber admin dashboard API.

Task: [YGMP1-91](https://saritasa.atlassian.net/browse/YGMP1-91)

### 0.12.0

- Add pagination for Chamber statistics API.

Task: [YGMP1-82](https://saritasa.atlassian.net/browse/YGMP1-82)

### 0.11.1

- Update Chamber CRUD endpoints for Super Admins.
- Split TRC coord name to 2 fields.

Task: [YGMP1-75](https://saritasa.atlassian.net/browse/YGMP1-75)

### 0.11.0

- Provide chamber login api and forgot password flow.

Task: [YGMP1-87](https://saritasa.atlassian.net/browse/YGMP1-87)

### 0.10.0

- Add Chamber CRUD endpoints for Super Admins.

Task: [YGMP1-75](https://saritasa.atlassian.net/browse/YGMP1-75)

### 0.9.0

- Add Chamber statistics API.

Task: [YGMP1-82](https://saritasa.atlassian.net/browse/YGMP1-82)

### 0.8.0

- Add API to check Chamber nickname uniqueness.

Task: [YGMP1-77](https://saritasa.atlassian.net/browse/YGMP1-77)

### 0.7.0

- Provide config for uploading files to s3.

Task: [YGMP1-85](https://saritasa.atlassian.net/browse/YGMP1-85)

### 0.6.0

- Add login endpoint for Super Admins.

Task: [YGMP1-71](https://saritasa.atlassian.net/browse/YGMP1-71)

### 0.5.0

- Add base schemes:
  - `v1/admin` for admin api resources.
  - `v1/chamber` for chamber api resources.
  - `v1/volunteer` for volunteer api resources.
- Add base viewsets with role-based permissions for resource types
  - `AdminBaseViewSet`
  - `ChamberBaseViewSet`
  - `VolunteerBaseViewSet`

Task: [YGMP1-48](https://saritasa.atlassian.net/browse/YGMP1-48)

### 0.4.0

- Add `campaigns` app.

Task: [YGMP1-42](https://saritasa.atlassian.net/browse/YGMP1-42)

### 0.3.0

- Add `chambers` app.

Task: [YGMP1-39](https://saritasa.atlassian.net/browse/YGMP1-39)

### 0.2.0

- Add `members` app.

Task: [YGMP1-41](https://saritasa.atlassian.net/browse/YGMP1-41)

### 0.1.0

- Add `resources` app.

Task: [YGMP1-43](https://saritasa.atlassian.net/browse/YGMP1-43)

### 0.0.0

- Project initialized.

Task: [YGMP1-36](https://saritasa.atlassian.net/browse/YGMP1-36)
