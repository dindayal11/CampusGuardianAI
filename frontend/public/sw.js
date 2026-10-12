self.addEventListener("push", (event) => {
  let payload = {};
  try {
    payload = event.data ? event.data.json() : {};
  } catch {
    payload = {
      title: "Campus Guardian AI",
      body: "You have a new notification.",
    };
  }
  const title = payload.title || "Campus Guardian AI";
  const options = {
    body: payload.body || "You have a new notification.",
    icon: "/campus-guardian-logo-v2.png",
    badge: "/favicon.png",
    data: {
      url:
        typeof payload.url === "string" &&
        payload.url.startsWith("/") &&
        !payload.url.startsWith("//")
          ? payload.url
          : "/dashboard/announcements",
    },
  };
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl =
    event.notification.data &&
    typeof event.notification.data.url === "string"
      ? event.notification.data.url
      : "/dashboard/announcements";
  event.waitUntil(
    self.clients.matchAll({
      type: "window",
      includeUncontrolled: true,
    }).then((clients) => {
      for (const client of clients) {
        if ("focus" in client) {
          client.navigate(targetUrl);
          return client.focus();
        }
      }
      return self.clients.openWindow(targetUrl);
    })
  );
});
