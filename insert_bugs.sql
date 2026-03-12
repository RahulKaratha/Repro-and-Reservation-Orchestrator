-- Insert Dummy Bugs (Copy-paste this into MySQL terminal)
-- Make sure you have engineers with IDs 2, 3, 4 or change the engineer_id values

-- Insert Repro Bugs
INSERT INTO Bugs (priority, bug_code, bug_type, engineer_id, summary, station_config, resource_group, status) VALUES
('P0', 'REPRO-2024-001', 'repro', 2, 'Critical application crash on startup', 'Config-A-Standard', 'Group-Alpha', 'pending'),
('P0', 'REPRO-2024-002', 'repro', 2, 'Security vulnerability in authentication flow', 'Config-B-Advanced', 'Group-Beta', 'running'),
('P1', 'REPRO-2024-003', 'repro', 3, 'Memory leak in data processing module', 'Config-C-Premium', 'Group-Alpha', 'pending'),
('P1', 'REPRO-2024-004', 'repro', 3, 'Database connection timeout under load', 'Config-A-Standard', 'Group-Gamma', 'scheduled'),
('P2', 'REPRO-2024-005', 'repro', 4, 'Performance degradation with large datasets', 'Config-D-Enterprise', 'Group-Beta', 'pending'),
('P2', 'REPRO-2024-006', 'repro', 4, 'UI rendering issue on high-resolution displays', 'Config-B-Advanced', 'Group-Delta', 'completed'),
('P3', 'REPRO-2024-007', 'repro', 2, 'Incorrect data validation in form submission', 'Config-E-Custom', 'Group-Alpha', 'pending'),
('P4', 'REPRO-2024-008', 'repro', 3, 'Minor text alignment issue in settings panel', 'Config-A-Standard', 'Group-Gamma', 'running');

-- Insert Test Bugs
INSERT INTO Bugs (priority, bug_code, bug_type, engineer_id, summary, station_config, resource_group, status) VALUES
('P0', 'TEST-2024-001', 'test', 2, 'Security penetration testing for API endpoints', 'Config-Test-1', 'Group-Alpha', 'pending'),
('P1', 'TEST-2024-002', 'test', 2, 'Load testing for concurrent user sessions', 'Config-Test-2', 'Group-Beta', 'scheduled'),
('P1', 'TEST-2024-003', 'test', 3, 'Performance benchmarking for database queries', 'Config-Test-3', 'Group-Alpha', 'pending'),
('P2', 'TEST-2024-004', 'test', 3, 'Integration testing with third-party services', 'Config-Test-1', 'Group-Gamma', 'running'),
('P2', 'TEST-2024-005', 'test', 4, 'Verify login functionality across browsers', 'Config-Test-4', 'Group-Beta', 'pending'),
('P3', 'TEST-2024-006', 'test', 4, 'Cross-platform compatibility testing', 'Config-Test-2', 'Group-Delta', 'completed'),
('P3', 'TEST-2024-007', 'test', 2, 'Test responsive design on mobile devices', 'Config-Test-5', 'Group-Alpha', 'pending'),
('P4', 'TEST-2024-008', 'test', 3, 'UI accessibility compliance testing', 'Config-Test-3', 'Group-Gamma', 'scheduled');

-- Insert Bug Tests
INSERT INTO Bug_Tests (bug_id, test_name) VALUES
(1, 'Smoke Test'), (1, 'Regression Test'),
(2, 'Security Test'), (2, 'Penetration Test'),
(3, 'Performance Test'), (3, 'Load Test'),
(4, 'Integration Test'), (4, 'Unit Test'),
(5, 'API Test'), (5, 'UI Test'),
(6, 'Regression Test'), (6, 'Performance Test'),
(7, 'Smoke Test'), (7, 'Integration Test'),
(8, 'Unit Test'), (8, 'API Test'),
(9, 'Security Test'), (9, 'API Test'),
(10, 'Load Test'), (10, 'Stress Test'),
(11, 'Performance Test'), (11, 'Benchmark Test'),
(12, 'Integration Test'), (12, 'API Test'),
(13, 'Functional Test'), (13, 'Smoke Test'),
(14, 'Compatibility Test'), (14, 'Integration Test'),
(15, 'UI Test'), (15, 'Responsive Test'),
(16, 'Accessibility Test'), (16, 'Compliance Test');

-- Insert Bug Stations
INSERT INTO Bug_stations (bug_id, station_name) VALUES
(1, 'Station-A1'), (1, 'Station-A2'),
(2, 'Station-B1'), (2, 'Station-B2'), (2, 'Station-B3'),
(3, 'Station-C1'), (3, 'Station-C2'),
(4, 'Station-D1'), (4, 'Station-D2'),
(5, 'Station-E1'), (5, 'Station-E2'), (5, 'Station-E3'),
(6, 'Station-F1'), (6, 'Station-F2'),
(7, 'Station-G1'), (7, 'Station-G2'),
(8, 'Station-H1'), (8, 'Station-H2'),
(9, 'Test-Station-1'), (9, 'Test-Station-2'),
(10, 'Test-Station-3'), (10, 'Test-Station-4'),
(11, 'Test-Station-5'), (11, 'Test-Station-6'),
(12, 'Test-Station-7'), (12, 'Test-Station-8'),
(13, 'Test-Station-9'), (13, 'Test-Station-10'),
(14, 'Test-Station-11'), (14, 'Test-Station-12'),
(15, 'Test-Station-13'), (15, 'Test-Station-14'),
(16, 'Test-Station-15'), (16, 'Test-Station-16');
