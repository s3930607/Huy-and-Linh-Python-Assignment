DELETE FROM MissionStatement;
INSERT INTO MissionStatement (id, heading, body, display_order) VALUES
    (1, 'Our purpose',      'Many high school students move away from home when they start university, and for the first time they have to look after their own health without a parent nearby. We built this site so those students can see how serious measles, rubella and pertussis actually are, and which vaccines are used against them. These three diseases are common and well understood, which makes them a sensible place to start. What someone learns here is also worth carrying forward, for their own children later on.', 1),
    (2, 'How to use this site', 'Start on the home page for a snapshot of what the data covers. Vaccination rates shows which countries reached their target for one vaccine in one year, and how each region compares. Infection by economy shows reported cases per 100,000 people for one disease and one income group. Improvement ranks the countries whose vaccination rate rose the most between two chosen years. Above average lists every country reporting a higher infection rate than the global figure.',     2);

DELETE FROM Persona;
INSERT INTO Persona (name, role, age, goal, frustration, tech_skill) VALUES
    ('Minh', 'High school student', 17,
     'Learn what the three preventable diseases are, which vaccines are in use, and where they are used most',
     'Cannot compare one country against another, and the WHO figures are hard to read',
     'Low to medium');

DELETE FROM TeamMember;
INSERT INTO TeamMember (StudentID, full_name, role, subtask) VALUES
    ('S3930607', 'Hoang Quoc Huy', 'Code', 'A'),
    ('S4205952', 'Linh Nguyen Ha Phuong', 'Code', 'B');
