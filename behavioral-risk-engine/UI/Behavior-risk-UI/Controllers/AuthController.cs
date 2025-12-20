using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authentication;
using System.Security.Claims;
using Behavior_risk_UI.Models;

namespace Behavior_risk_UI.Controllers
{
    public class AuthController : Controller
    {
        // TEMPORARY MVP USERS
        private readonly Dictionary<string, string> _users = new()
        {
            { "admin", "admin123" },
            { "moderator", "mod123" }
        };

        [HttpGet]
        public IActionResult Login()
        {
            return View(new LoginViewModel());
        }
        [HttpGet]
        public IActionResult NotAuthorized()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> Login(LoginViewModel model)
        {
            if (!ModelState.IsValid)
                return View(model);

            if (!_users.TryGetValue(model.Username, out var pwd) || pwd != model.Password)
            {
                model.Error = "Invalid username or password";
                return View(model);
            }

            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.Name, model.Username),
                new Claim(ClaimTypes.Role, model.Username == "admin" ? "Admin" : "Moderator")
            };

            var identity = new ClaimsIdentity(claims, "AuthCookie");
            var principal = new ClaimsPrincipal(identity);

            await HttpContext.SignInAsync("AuthCookie", principal);

            return RedirectToAction("Index", "Home");
        }

        public async Task<IActionResult> Logout()
        {
            await HttpContext.SignOutAsync("AuthCookie");
            return RedirectToAction("Login");
        }
    }
}