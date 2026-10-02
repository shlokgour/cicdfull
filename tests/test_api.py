def make_course(client, title="Python 101"):
    return client.post("/courses", json={"title": title, "description": "intro"}).json()


def make_student(client, email="a@b.com"):
    return client.post("/students", json={"name": "Asha", "email": email}).json()


def test_health_and_metrics(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200
    assert b"http_requests_total" in client.get("/metrics").content


def test_course_crud(client):
    c = make_course(client)
    assert c["title"] == "Python 101"
    assert client.get(f"/courses/{c['id']}").status_code == 200
    r = client.put(f"/courses/{c['id']}", json={"title": "Python 102"})
    assert r.json()["title"] == "Python 102"
    assert client.delete(f"/courses/{c['id']}").status_code == 204
    assert client.get(f"/courses/{c['id']}").status_code == 404


def test_course_validation(client):
    assert client.post("/courses", json={"title": ""}).status_code == 422


def test_student_unique_email(client):
    make_student(client)
    r = client.post("/students", json={"name": "B", "email": "a@b.com"})
    assert r.status_code == 409


def test_student_invalid_email(client):
    r = client.post("/students", json={"name": "B", "email": "nope"})
    assert r.status_code == 422


def test_content_lifecycle(client):
    c = make_course(client)
    r = client.post(f"/courses/{c['id']}/contents",
                    json={"title": "Intro", "body": "hello", "content_type": "video"})
    assert r.status_code == 201
    cid = r.json()["id"]
    assert len(client.get(f"/courses/{c['id']}/contents").json()) == 1
    assert client.delete(f"/courses/{c['id']}/contents/{cid}").status_code == 204
    assert client.get(f"/courses/{c['id']}/contents").json() == []


def test_content_bad_type(client):
    c = make_course(client)
    r = client.post(f"/courses/{c['id']}/contents", json={"title": "x", "content_type": "bad"})
    assert r.status_code == 422


def test_enrollment(client):
    c, s = make_course(client), make_student(client)
    assert client.post(f"/students/{s['id']}/enroll/{c['id']}").status_code == 204
    client.post(f"/students/{s['id']}/enroll/{c['id']}")  # idempotent
    assert len(client.get(f"/courses/{c['id']}/students").json()) == 1
    assert len(client.get(f"/students/{s['id']}").json()["courses"]) == 1


def test_enroll_missing(client):
    s = make_student(client)
    assert client.post(f"/students/{s['id']}/enroll/999").status_code == 404
