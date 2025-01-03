// Generate raster favicons from app/icon.svg into public/
// Requires devDependencies: sharp, png-to-ico
import fs from 'node:fs/promises'
import path from 'node:path'
import sharp from 'sharp'
import pngToIco from 'png-to-ico'

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true })
}

async function run() {
  const projectRoot = process.cwd()
  const svgPath = path.join(projectRoot, 'src', 'app', 'icon.svg')
  const publicDir = path.join(projectRoot, 'public')
  await ensureDir(publicDir)

  // Verify SVG exists
  try {
    await fs.access(svgPath)
  } catch {
    throw new Error(`SVG not found at ${svgPath}`)
  }

  // Target files
  const files = {
    png32: path.join(publicDir, 'favicon-32x32.png'),
    apple: path.join(publicDir, 'apple-touch-icon.png'),
    icon192: path.join(publicDir, 'icon-192.png'),
    icon512: path.join(publicDir, 'icon-512.png'),
    ico: path.join(publicDir, 'favicon.ico'),
  }

  // Generate base PNGs using sharp
  await sharp(svgPath).resize(32, 32).png({ compressionLevel: 9 }).toFile(files.png32)
  await sharp(svgPath).resize(180, 180).png({ compressionLevel: 9 }).toFile(files.apple)
  await sharp(svgPath).resize(192, 192).png({ compressionLevel: 9 }).toFile(files.icon192)
  await sharp(svgPath).resize(512, 512).png({ compressionLevel: 9 }).toFile(files.icon512)

  // ICO: combine 16, 32, 48 sizes
  const png16 = await sharp(svgPath).resize(16, 16).png({ compressionLevel: 9 }).toBuffer()
  const png32 = await sharp(svgPath).resize(32, 32).png({ compressionLevel: 9 }).toBuffer()
  const png48 = await sharp(svgPath).resize(48, 48).png({ compressionLevel: 9 }).toBuffer()
  const icoBuf = await pngToIco([png16, png32, png48])
  await fs.writeFile(files.ico, icoBuf)

  const created = Object.values(files).map(f => path.relative(projectRoot, f)).join('\n - ')
  console.log('Generated favicon assets:\n - ' + created)
}

run().catch((err) => {
  console.error(err)
  process.exit(1)
})
