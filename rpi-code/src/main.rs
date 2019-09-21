use std::env;
use std::io::{self, Write};

use hyper::http::Request;
use hyper::rt::{self, Future, Stream};

use std::time::Duration;

// Every minute polling
const POLLING_PERIOD: u64 = 60;

fn main() {
    // Some simple CLI args requirements...
    let url = match env::args().nth(1) {
        Some(url) => url,
        None => {
            println!("Usage: client <url>");
            return;
        }
    };

    let api_key = match env::var("API_GATEWAY_KEY") {
        Ok(val) => val,
        Err(e) => {
            println!("Could get API_GATEWAY_KEY env variable = {:?}", e);
            return;
        }
    };

    // HTTPS requires picking a TLS implementation, so give a better
    // warning if the user tries to request an 'https' URL.
    let url = url.parse::<hyper::Uri>().unwrap();

    let duration = Duration::from_secs(POLLING_PERIOD);

    for _ in 0..5 {
        // Run the runtime with the future trying to fetch and print this URL.
        //
        // Note that in more complicated use cases, the runtime should probably
        // run on its own, and futures should just be spawned into it.
        rt::run(fetch_url(url.clone(), &api_key));
        std::thread::sleep(duration);
    }
}

fn fetch_url(url: hyper::Uri, api_key: &str) -> impl Future<Item = (), Error = ()> {
    let https = hyper_tls::HttpsConnector::new(4).unwrap();
    let client = hyper::Client::builder().build::<_, hyper::Body>(https);

    let mut request = Request::builder();
    let request = request
        .uri(url)
        .header("x-api-key", api_key)
        .body(hyper::Body::from(""))
        .unwrap();
    client
        .request(request)
        // Fetch the url...
        // And then, if we get a response back...
        .and_then(|res| {
            println!("Response: {}", res.status());
            println!("Headers: {:#?}", res.headers());

            // The body is a stream, and for_each returns a new Future
            // when the stream is finished, and calls the closure on
            // each chunk of the body...
            res.into_body().for_each(|chunk| {
                io::stdout()
                    .write_all(&chunk)
                    .map_err(|e| panic!("example expects stdout is open, error={}", e))
            })
        })
        // If all good, just tell the user...
        .map(|_| {
            println!("\n\nDone.");
        })
        // If there was an error, let the user know...
        .map_err(|err| {
            eprintln!("Error {}", err);
        })
}
