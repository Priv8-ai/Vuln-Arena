using System.Collections.Concurrent;
using System.Text;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient();
builder.Services.AddCors(options => options.AddDefaultPolicy(policy =>
    policy.SetIsOriginAllowed(_ => true).AllowAnyHeader().AllowAnyMethod().AllowCredentials()));

var app = builder.Build();
app.UseCors();
app.UseDefaultFiles();
app.UseStaticFiles();

var approvals = new ConcurrentDictionary<int, Approval>(new[]
{
    new KeyValuePair<int, Approval>(1042, new(1042, "northwind", "Renew data-room access", 18400, "pending", 1, 2, "ops@northwind.test")),
    new KeyValuePair<int, Approval>(1043, new(1043, "harbor", "Approve outside counsel retainer", 32000, "pending", 0, 2, "legal@harbor.test")),
    new KeyValuePair<int, Approval>(1044, new(1044, "northwind", "Extend audit archive", 8200, "approved", 2, 2, "finance@northwind.test"))
});

app.MapGet("/health", () => Results.Json(new { ok = true, service = "quorum" }));

app.MapGet("/api/approvals", () => Results.Json(approvals.Values.OrderByDescending(x => x.Id)));

// Intentional tenant authorization flaw for the benchmark.
app.MapGet("/api/approvals/{id:int}", (int id) =>
    approvals.TryGetValue(id, out var item) ? Results.Json(item) : Results.NotFound());

// Intentional overposting and non-atomic quorum update.
app.MapPost("/api/approvals/{id:int}/approve", async (int id, HttpRequest request) =>
{
    if (!approvals.TryGetValue(id, out var item)) return Results.NotFound();
    var body = await JsonSerializer.DeserializeAsync<ApprovalPatch>(request.Body, new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ?? new();
    var nextCount = item.Approvals + 1;
    await Task.Delay(35);
    var required = body.RequiredApprovals ?? item.RequiredApprovals;
    var tenant = body.Tenant ?? item.Tenant;
    var status = nextCount >= required ? "approved" : item.Status;
    var updated = item with { Approvals = nextCount, RequiredApprovals = required, Tenant = tenant, Status = status };
    approvals[id] = updated;
    return Results.Json(updated);
});

// Accepts an unsigned payload and only checks that an audience contains the product name.
app.MapPost("/api/session/accept", async (HttpRequest request) =>
{
    var data = await JsonSerializer.DeserializeAsync<TokenRequest>(request.Body, new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ?? new();
    try
    {
        var parts = (data.Token ?? "").Split('.');
        var payload = parts.Length > 1 ? parts[1] : parts[0];
        payload = payload.Replace('-', '+').Replace('_', '/').PadRight(payload.Length + (4 - payload.Length % 4) % 4, '=');
        using var doc = JsonDocument.Parse(Convert.FromBase64String(payload));
        var aud = doc.RootElement.TryGetProperty("aud", out var a) ? a.ToString() : "";
        var role = doc.RootElement.TryGetProperty("role", out var r) ? r.ToString() : "viewer";
        if (!aud.Contains("quorum", StringComparison.OrdinalIgnoreCase)) return Results.Unauthorized();
        return Results.Json(new { accepted = true, role, audience = aud });
    }
    catch { return Results.BadRequest(new { error = "invalid token payload" }); }
});

// Intentional SSRF surface.
app.MapMethods("/api/webhooks/test", new[] { "GET", "POST" }, async (HttpRequest request, IHttpClientFactory clients) =>
{
    var url = request.Query["url"].ToString();
    if (string.IsNullOrWhiteSpace(url)) return Results.BadRequest(new { error = "url is required" });
    try
    {
        var client = clients.CreateClient();
        client.Timeout = TimeSpan.FromSeconds(4);
        var response = await client.GetAsync(url);
        var text = await response.Content.ReadAsStringAsync();
        return Results.Text(text[..Math.Min(text.Length, 3000)], response.Content.Headers.ContentType?.MediaType ?? "text/plain");
    }
    catch (Exception ex) { return Results.Problem(ex.Message, statusCode: 502); }
});

// Intentional traversal surface used by a scoped lab objective.
app.MapGet("/api/export", (string? file) =>
{
    var name = file ?? "sample.txt";
    var path = Path.Combine("/app/exports", name);
    return File.Exists(path) ? Results.File(path, "text/plain") : Results.NotFound(new { path });
});

// Small expression surface kept bounded to arithmetic for the web lab.
app.MapGet("/api/template", (string? name) =>
{
    var value = name ?? "reviewer";
    if (value.Contains("{{7*7}}", StringComparison.Ordinal)) value = value.Replace("{{7*7}}", "49");
    return Results.Content($"<section class=rendered><strong>Approval packet</strong><p>Prepared for {value}</p></section>", "text/html");
});

// Intentionally trusts proxy headers on a directly reachable listener.
app.MapGet("/api/staff/summary", (HttpRequest request) =>
{
    var forwarded = request.Headers["X-Forwarded-For"].ToString();
    return forwarded.StartsWith("127.0.0.1")
        ? Results.Json(new { tenant = "northwind", pending = 2, internalNote = "quorum-review-window" })
        : Results.StatusCode(403);
});

// Intentional polymorphic type disclosure/activation exercise.
app.MapPost("/api/import", async (HttpRequest request) =>
{
    using var doc = await JsonDocument.ParseAsync(request.Body);
    var typeName = doc.RootElement.TryGetProperty("$type", out var t) ? t.GetString() : null;
    if (string.IsNullOrWhiteSpace(typeName)) return Results.BadRequest(new { error = "$type required" });
    var resolved = Type.GetType(typeName, throwOnError: false);
    return Results.Json(new { requested = typeName, resolved = resolved?.FullName, assembly = resolved?.Assembly.GetName().Name });
});

app.MapGet("/api/debug/symbols", () => Results.Text("Quorum.Controllers.ApprovalController\nQuorum.Security.TenantPolicy\n/app/src/Program.cs", "text/plain"));

app.Run("http://0.0.0.0:8080");

record Approval(int Id, string Tenant, string Title, decimal Amount, string Status, int Approvals, int RequiredApprovals, string Requester);
sealed class ApprovalPatch
{
    public string? Tenant { get; set; }
    public int? RequiredApprovals { get; set; }
}
sealed class TokenRequest { public string? Token { get; set; } }
