// fn: check if a value is a string, and throw an error if not
function getStrOrError(str: any): string {
    if (typeof str !== 'string') {
        throw new Error(`Expected string, got ${typeof str}`);
    }

    return str;
}

export {
    getStrOrError,
}