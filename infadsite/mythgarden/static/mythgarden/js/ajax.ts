import Cookies from "js-cookie";

// fn: given a post url and a data object, make an xhr call to the server and return the response
function post(url: string, data: object): Promise<Response> {
    const csrftoken = getStrOrError(Cookies.get('csrftoken'));

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', url);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
        xhr.send(JSON.stringify(data));

        xhr.onload = () => {
            if (xhr.status === 200) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(xhr.responseText);
            }
        };
    });
}

export {
    post,
}