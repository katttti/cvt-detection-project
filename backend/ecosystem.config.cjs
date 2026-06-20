module.exports = {
  apps: [
    {
      name: "cvt-api",
      cwd: "/Users/katykim/Desktop/Finnect-challenge/cvt-detection-project",
      script: "backend/.venv/bin/python",
      args: "-m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000",
      env: {
        CVT_SHARED_PASSWORD: "replace-me",
      },
    },
    {
      name: "cvt-ops",
      cwd: "/Users/katykim/Desktop/Finnect-challenge/cvt-detection-project",
      script: "backend/.venv/bin/python",
      args: "-m uvicorn backend.app.ops:ops_app --host 127.0.0.1 --port 3000",
      env: {
        CVT_SHARED_PASSWORD: "replace-me",
        CVT_OPS_USERNAME: "friend",
      },
    },
  ],
};
