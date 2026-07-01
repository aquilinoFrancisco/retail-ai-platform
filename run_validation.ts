import { execSync, spawn } from "child_process";
import * as path from "path";
import * as fs from "fs";
import * as https from "https";

function downloadFile(url: string, dest: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }
      response.pipe(file);
      file.on("finish", () => {
        file.close();
        resolve();
      });
    }).on("error", (err) => {
      try { fs.unlinkSync(dest); } catch {}
      reject(err);
    });
  });
}

async function main() {
  console.log("Preparing Python environment...");
  
  // Try to see if pip can be bootstrapped via get-pip.py
  try {
    const getPipPath = path.join(process.cwd(), "get-pip.py");
    if (!fs.existsSync(getPipPath)) {
      console.log("Downloading get-pip.py...");
      await downloadFile("https://bootstrap.pypa.io/get-pip.py", getPipPath);
      console.log("Downloaded successfully.");
    }
    
    console.log("Running get-pip.py...");
    execSync("python3 get-pip.py --user --break-system-packages", { stdio: "inherit" });
    
    console.log("Installing Pydantic package...");
    execSync("python3 -m pip install pydantic --user --break-system-packages", { stdio: "inherit" });
    
    console.log("Installing LangGraph and CrewAI packages...");
    try {
      execSync("python3 -m pip install langgraph crewai --user --break-system-packages", { stdio: "inherit" });
    } catch (e) {
      console.log("Warning: LangGraph/CrewAI installation failed:", e);
    }
  } catch (err) {
    console.error("Warning: local pip bootstrap or install failed:", err);
  }

  // Ensure python3 can find the user site packages
  // We can add the user site packages path directly to Python's sys.path or process.env
  const env = { ...process.env };
  
  const pythonProcess = spawn("python3", ["validate_mcp.py"], {
    cwd: path.join(process.cwd(), "retail-agentic-platform"),
    stdio: "inherit",
    env
  });

  pythonProcess.on("close", (code) => {
    process.exit(code ?? 0);
  });
}

main().catch((err) => {
  console.error("Fatal error in validator runner:", err);
  process.exit(1);
});
