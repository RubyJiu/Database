

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE publishers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NULL
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    author VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT NOT NULL,
    publisher_id INT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (id),
    FOREIGN KEY (publisher_id) REFERENCES publishers (id) ON DELETE SET NULL
);


INSERT INTO categories (name) VALUES ('Fiction'), ('Non-Fiction'), ('Romance');

INSERT INTO publishers (name, country) VALUES
('O\'Reilly Media', 'USA'),
('Gramedia', 'Indonesia');

INSERT INTO books (name, description, author, price, category_id)
VALUES
    ('The Great Gatsby', 'A classic novel about the American Dream', 'F. Scott Fitzgerald', 19.99, 1),
    ('The Catcher in the Rye', 'A classic coming-of-age novel', 'J.D. Salinger', 14.99, 1),
    ('To Kill a Mockingbird', 'A Pulitzer Prize-winning novel about racial injustice', 'Harper Lee', 17.99, 1),
    ('Essays on the Art of Writing', 'A collection of essays by Ernest Hemingway', 'Ernest Hemingway', 12.99, 2),
    ('The Hitchhiker\'s Guide to the Galaxy', 'A science fiction comedy', 'Douglas Adams', 14.99, 1),
    ('The Handmaid\'s Tale', 'A dystopian novel about a totalitarian society', 'Margaret Atwood', 16.99, 1),
    ('Dune', 'A science fiction classic', 'Frank Herbert', 12.99, 1),
    ('The Da Vinci Code', 'A thriller about a conspiracy', 'Dan Brown', 17.99, 1),
    ('The Hunger Games', 'A dystopian trilogy', 'Suzanne Collins', 12.99, 1),
    ('Harry Potter and the Philosopher\'s Stone', 'The first book in the Harry Potter series', 'J.K. Rowling', 12.99, 1);
