USE ShortStories;

CREATE TABLE Stories (
        Id varchar(255) PRIMARY KEY,
        Link varchar(255) NOT NULL,
        Title varchar(255) NOT NULL,
        Summary text NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE Subscriptions (
        Name varchar(255),
        Story_Id varchar(255) NOT NULL,
        Chapter int NOT NULL,
        Section int NOT NULL,
        Last_Read int NOT NULL,
        Paragraphs_Per_Read int NOT NULL,
        Day int NOT NULL,
        PRIMARY KEY (Name, Story_Id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ;
CREATE TABLE StoryContent (
        Id varchar(255) NOT NULL,
        Chapter int NOT NULL,
        Section int NOT NULL,
        Paragraph text NOT NULL,
        PRIMARY KEY (Id, Chapter, Section)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ;