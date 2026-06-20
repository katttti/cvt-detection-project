const sharedPassword = process.env.CVT_SHARED_PASSWORD || "replace-me";
const opsUsername = process.env.CVT_OPS_USERNAME || "friend";

module.exports = {
  apps: [
    {
      name: "cvt-api",
      cwd: "/Users/katykim/Desktop/Finnect-challenge/cvt-detection-project",
      script: "backend/.venv/bin/python",
      args: "-m uvicorn backend.app.main:app --host 0.0.0.0 --port 3000",
      env: {
        CVT_SHARED_PASSWORD: sharedPassword,
      },
    },
    {
      name: "cvt-ops",
      cwd: "/Users/katykim/Desktop/Finnect-challenge/cvt-detection-project",
      script: "backend/.venv/bin/python",
      args: "-m uvicorn backend.app.ops:ops_app --host 0.0.0.0 --port 3001",
      env: {
        CVT_SHARED_PASSWORD: sharedPassword,
        CVT_OPS_USERNAME: opsUsername,
      },
    },
  ],
};
