using Microsoft.AspNetCore.Authentication.Cookies;
using Behavior_risk_UI.mappers;

var builder = WebApplication.CreateBuilder(args);

/* ============================
   AUTHENTICATION & AUTHORIZATION
   ============================ */

builder.Services
    .AddAuthentication("AuthCookie")
    .AddCookie("AuthCookie", options =>
    {
        options.LoginPath = "/Auth/Login";
        options.LogoutPath = "/Auth/Logout";
        options.AccessDeniedPath = "/Auth/NotAuthorized";

        options.ExpireTimeSpan = TimeSpan.FromHours(8);
        options.SlidingExpiration = true;

        // 🔑 CRITICAL PART: override default redirect
        options.Events = new CookieAuthenticationEvents
        {
            OnRedirectToLogin = context =>
            {
                context.Response.Redirect("/Auth/NotAuthorized");
                return Task.CompletedTask;
            }
        };
    });

builder.Services.AddAuthorization();

/* ============================
   HTTP CLIENT (FastAPI backend)
   ============================ */

builder.Services.AddHttpClient<ApiClient>(client =>
{
    client.BaseAddress = new Uri("http://localhost:8000"); // FastAPI URL
    client.Timeout = TimeSpan.FromSeconds(25);
});

/* ============================
   JSON CONFIG (snake_case API)
   ============================ */

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.PropertyNamingPolicy =
        System.Text.Json.JsonNamingPolicy.SnakeCaseLower;
});

/* ============================
   MVC
   ============================ */

builder.Services.AddControllersWithViews();

/* ============================
   BUILD APP
   ============================ */

var app = builder.Build();

/* ============================
   MIDDLEWARE PIPELINE
   ============================ */

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

// ⚠️ ORDER MATTERS
app.UseAuthentication();
app.UseAuthorization();

/* ============================
   ROUTING
   ============================ */

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}"
);

app.Run();
