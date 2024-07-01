select fs.form_id ,f.description, u.fullname trainee, fs.created_at, u2.fullname observer
from FormSubmissions fs
inner join forms f on f.form_id = fs.form_id
inner join users u on u.username = fs.trainee_id
inner join users u2 on fs.observer_id = u2.id;
