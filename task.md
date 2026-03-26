# Manager Dashboard Bug Expansion Plan

## 1. Planning & Setup
- [x] Verify the DB migration state
- [x] Understand the schema of the new tables by reviewing the model files.
- [x] Analyze `mock_bugs.json` layout.

## 2. Ingestion Script creation
- [x] Create `scripts/ingest_mock_data.py`.
- [x] Implement DB connection and cleanup of existing data.
- [x] Parse `mock_bugs.json`.
- [x] Extract structured properties from `comment[0].text`
- [x] Populate `Bug_Tests`, `Bug_stations`, `Bug_Comments`.
- [x] Integrate with local Mock API (`http://localhost:5000/v2.8/call/chatlite`) to generate ML analysis and populate `ML_Analysis` table.

## 3. Backend API updates
- [x] Add `GET /api/bugs/<id>/tests` route to `app/routes/bugDashboard.py`.
- [x] Add `GET /api/bugs/<id>/analysis` route to `app/routes/bugDashboard.py`.

## 4. Frontend UI implementation
- [x] Modify `app/templates/bugManagement.html` main table UI to include the "Tests" column with a dropdown indicator.
- [x] Add JavaScript to handle the collapsable sub-rows for Tests and ML Analysis, fetching from the new endpoints.
- [x] Apply styling suitable for the sub-rows and the ML Analysis panel.

## 5. Verification
- [x] Run the ingest script end-to-end to verify data is correctly stored in the DB.
- [x] Open the web page and review the visual layout and expand actions.
- [x] Ensure ML Analysis text displays properly within the sub-rows.
