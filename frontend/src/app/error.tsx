"use client";
export default function Error({reset}:{reset:()=>void}){return <main className="page"><div className="container prose"><span className="eyebrow">Something went wrong</span><h1>We could not load this page.</h1><p>Please retry.</p><button className="btn primary" type="button" onClick={reset}>Try again</button></div></main>}
