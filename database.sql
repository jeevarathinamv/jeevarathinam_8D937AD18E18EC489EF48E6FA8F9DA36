-- Raja Raja Cholan Historical Information Website Database Schema
-- Database: raja_raja_cholan_db
-- Compatible with XAMPP MySQL and phpMyAdmin

CREATE DATABASE IF NOT EXISTS `raja_raja_cholan_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `raja_raja_cholan_db`;

-- 1. Admin Users Table
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Historical Articles Table
CREATE TABLE IF NOT EXISTS `articles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL,
    `category` VARCHAR(50) NOT NULL, -- history, military, temple, kingdom, achievements
    `era_year` VARCHAR(50) DEFAULT NULL,
    `summary` TEXT NOT NULL,
    `content` LONGTEXT NOT NULL,
    `image_url` VARCHAR(255) DEFAULT NULL,
    `is_featured` TINYINT(1) DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Gallery Table
CREATE TABLE IF NOT EXISTS `gallery` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(150) NOT NULL,
    `category` VARCHAR(50) NOT NULL, -- temple, portrait, architecture, sculptures, warfare
    `description` TEXT NOT NULL,
    `image_url` VARCHAR(255) NOT NULL,
    `attribution` VARCHAR(150) DEFAULT 'Historical Archive / Public Domain',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Quiz Questions Table
CREATE TABLE IF NOT EXISTS `quiz_questions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `question` TEXT NOT NULL,
    `option_a` VARCHAR(255) NOT NULL,
    `option_b` VARCHAR(255) NOT NULL,
    `option_c` VARCHAR(255) NOT NULL,
    `option_d` VARCHAR(255) NOT NULL,
    `correct_option` CHAR(1) NOT NULL, -- A, B, C, or D
    `explanation` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed Initial Admin User (Username: admin, Password: admin123)
-- Password hash generated using Werkzeug scrypt/pbkdf2
INSERT INTO `admins` (`username`, `password_hash`, `full_name`, `email`) VALUES
('admin', 'scrypt:32768:8:1$E4q8dJ5QoF02wH91$7289f898ad36f4c5409cb69614451000632b842dfb0a312ba37a4d52bc8d5fa95786b6a67f67ad84b71ffc6f85ffaa421be0d517ea5cfcbaf1a0a52dfdb0bb2a', 'Chola Historian Administrator', 'admin@cholaheritage.org')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed Historical Articles
INSERT INTO `articles` (`title`, `category`, `era_year`, `summary`, `content`, `image_url`, `is_featured`) VALUES
('The Ascent of Arulmozhivarman', 'history', '947 – 985 CE', 'Born as Arulmozhivarman, the prince stepped aside in favor of Uttama Chola before peacefully ascending the imperial throne as Raja Raja Cholan I.', 'Arulmozhivarman was born in Tirukoilur as the third child of Parantaka Sundara Chola and Queen Vanavan Mahadevi of the Malayaman dynasty. Following the mysterious demise of his heroic elder brother Aditya Karikalan, Tamil country was poised on the verge of civil unrest. Exhibiting profound magnanimity and statecraft, Arulmozhivarman declined immediate accession to honor his uncle Uttama Chola throne claim. In 985 CE, upon Uttama Cholas passing, he ascended the throne under the regnal title Rajakesari Arulmozhi Varman, heralding the golden era of the Chola Empire.', '/static/images/rajaraja_portrait.svg', 1),

('Architectural Grandeur of Brihadeeswarar Temple', 'temple', '1003 – 1010 CE', 'Commissioned by Raja Raja Cholan, the Peruvudaiyar Kovil remains an engineering marvel with its 216-foot granite Vimana and 80-ton single stone Kumbam.', 'The Brihadeeswarar Temple (Peruvudaiyar Kovil) at Thanjavur is the pinnacle of Dravidian architectural mastery. Consecrated on the 275th day of his 25th regnal year in 1010 CE, the entire temple was erected using over 130,000 tons of granite in a delta plain devoid of natural stone. The colossal Vimana towers 216 feet into the sky, capped by an 80-ton monolithic granite cupola rolled into position across a 6-kilometer earthen ramp. Inscribed upon its walls are the names of every architect, stonemason, dancer, and singer who contributed, immortalizing their labor forever.', '/static/images/thanjavur_temple.svg', 1),

('Maritime Navy and Kandalur Salai Triumph', 'military', '988 – 1008 CE', 'The Chola navy was one of the most formidable maritime fleets in Asian history, neutralizing Chera naval fleets and expanding imperial boundaries.', 'Raja Raja Cholan realized that control of Indian Ocean trade sea-lanes required an invincible maritime armada. His historic campaign against Kandalur Salai dismantled the Chera naval stronghold, establishing undisputed supremacy along the Malabar and Coromandel coasts. Subsequent maritime expeditions incorporated Anuradhapura and the northern territories of Sri Lanka (renamed Mummudi Chola Mandalam) as well as the Maldives (Munnir Pazhantivu Pannirayiram). These naval conquests safeguarded Tamil merchant guilds venturing to Srivijaya and the Song Empire of China.', '/static/images/chola_navy.svg', 1),

('Revolutionary Revenue Survey and Administrative Division', 'kingdom', '986 – 1014 CE', 'Raja Raja Cholan implemented the historic land survey project in 1000 CE, classifying land quality and instituting democratic Ur and Sabha self-governance.', 'A master administrator, Raja Raja Cholan standardized revenue assessment through a comprehensive land survey across the entire empire, directed by his revenue minister Senapathi Kuravan Ulagalanthan. The kingdom was methodically divided into Valanadus, Nadus, and Urs. Inscriptions reveal the operation of autonomous village assemblies with strict eligibility criteria for village officials, fostering civic accountability, advanced canal irrigation maintenance, and famine relief granaries.', '/static/images/administration.svg', 1),

('Recovery of the Sacred Thevaram Hymns', 'achievements', 'c. 1000 CE', 'Recognizing the danger of losing Saivite devotional literature, Raja Raja assisted Nambiyandar Nambi to unearth the sacred Thevaram palm leaves from Chidambaram.', 'One of Raja Raja Cholan most revered cultural contributions was the salvage and compilation of the Thevaram devotional hymns composed by Appar, Sambandar, and Sundarar. Locked away in an inner chamber behind sealed doors at the Chidambaram Nataraja Temple, the precious palm leaf manuscripts were decomposing. Raja Raja facilitated their respectful retrieval and engaged court musicians (Odhuvars) to set them to classical Pann modes, earning him the honorific title Tirumurai Kanda Cholan.', '/static/images/nataraja_bronze.svg', 1);

-- Seed Gallery Items
INSERT INTO `gallery` (`title`, `category`, `description`, `image_url`, `attribution`) VALUES
('Imperial Portrait of Emperor Raja Raja Cholan', 'portrait', 'Artistic historical visualization of Emperor Raja Raja Cholan adorned in royal regalia, pearl garlands, and the imperial Chola crown.', '/static/images/rajaraja_portrait.svg', 'Original Chola Heritage Vector Art (CC-BY-4.0)'),
('Brihadeeswarar Temple - Tower of Majesty', 'temple', 'The imposing 216-foot Dravidian Vimana of Thanjavur Big Temple illuminated under the golden twilight sky.', '/static/images/thanjavur_temple.svg', 'Architectural Heritage Survey (Public Domain / Original)'),
('Chola Royal Navy Fleet in the Bay of Bengal', 'warfare', 'Ancient Tamil war vessels navigating high seas with multi-oared galleys and heraldic tiger flags unfurled.', '/static/images/chola_navy.svg', 'Maritime History Archive (Original Illustration)'),
('Sacred Bronze Nataraja of Chola Foundry', 'sculptures', 'World-celebrated lost-wax bronze sculpture of Lord Shiva in Ananda Tandava stance, epitomizing Chola artistic zenith.', '/static/images/nataraja_bronze.svg', 'Chola Bronze Metallurgy Collection (CC0)'),
('Imperial Tiger Seal and Ancient Coinage', 'architecture', 'The iconic Royal Chola royal crest featuring the seated tiger flanked by Pandya double fish and Chera bow emblem.', '/static/images/chola_emblem.svg', 'Numismatic Society of South India Archive');

-- Seed Quiz Questions
INSERT INTO `quiz_questions` (`question`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_option`, `explanation`) VALUES
('What was the original birth name of Emperor Raja Raja Cholan I before his coronation?', 'Aditya Karikalan', 'Arulmozhivarman', 'Kulothunga', 'Rajendra', 'B', 'Raja Raja Cholan was originally named Arulmozhivarman, meaning "he whose speech is graced with benevolence".'),
('In which year was the Brihadeeswarar Temple in Thanjavur consecrated by Raja Raja Cholan?', '985 CE', '1000 CE', '1010 CE', '1025 CE', 'C', 'The temple was consecrated on the 275th day of his 25th regnal year, which corresponds to 1010 CE.'),
('Which title was bestowed upon Raja Raja Cholan for recovering and organizing the sacred Thevaram hymns?', 'Mummudi Cholan', 'Tirumurai Kanda Cholan', 'Jayamgonda Cholan', 'Sivapadasekhara', 'B', 'He was celebrated as "Tirumurai Kanda Cholan" (The one who discovered and organized the sacred Shaivite scriptures).'),
('What is the approximate weight of the monolithic granite cupola sitting atop the Vimana of the Thanjavur Big Temple?', '20 Tons', '45 Tons', '80 Tons', '150 Tons', 'C', 'The monolithic granite capstone (Kumbam) weighs an astonishing 80 tons, hauled via a gentle ramp system.'),
('Which naval battle is prominently recorded in Raja Raja Cholan inscriptions celebrating his early maritime conquest?', 'Battle of Takkolam', 'Kandalur Salai', 'Battle of Venni', 'Koppam Campaign', 'B', 'The conquest of Kandalur Salai (Kandalur Salai Kalamarutha) is eulogized in his royal inscriptions as his first major naval victory.'),
('Which island kingdom was conquered and designated as "Mummudi Chola Mandalam" under Raja Raja Cholan rule?', 'Maldives', 'Java', 'Sri Lanka (Ceylon)', 'Sumatra', 'C', 'Northern Sri Lanka was incorporated into the Chola Empire as the province of Mummudi Chola Mandalam, with Polonnaruwa as capital.'),
('What was the name of the revenue minister who led the historic imperial land survey of 1000 CE under Raja Raja Cholan?', 'Aniruddha Brahmadhiraja', 'Senapathi Kuravan Ulagalanthan', 'Bana Vidyadhara', 'Nambiyandar Nambi', 'B', 'Senapathi Kuravan Ulagalanthan directed the metric survey and valuation of agricultural lands across the empire.'),
('What royal emblem appeared on the official seal and standard of the Imperial Cholas?', 'Bow and Arrow', 'Double Fish', 'Ferocious Tiger', 'Elephant', 'C', 'The leaping Tiger was the majestic dynastic emblem of the Cholas, often shown flanked by the fish of Pandyas and bow of Cheras.');
