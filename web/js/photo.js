import { esc } from "./shared.js";

const TYPES = ["image/png", "image/jpeg", "image/webp"];
const MAX_FILE_BYTES = 10 * 1024 * 1024;
const SIZE = 256;

// Center-crops and shrinks the picked image to a 256px JPEG data URL (well under the API's 256 KB limit).
export async function toAvatarDataUrl(file) {
  if (!TYPES.includes(file.type)) throw new Error("Pick a PNG, JPEG or WebP image.");
  if (file.size > MAX_FILE_BYTES) throw new Error("That image is over 10 MB. Pick a smaller one.");

  let bitmap;
  try {
    bitmap = await createImageBitmap(file);
  } catch {
    throw new Error("Couldn't read that image. Try another file.");
  }
  const side = Math.min(bitmap.width, bitmap.height);
  const canvas = Object.assign(document.createElement("canvas"), { width: SIZE, height: SIZE });
  canvas.getContext("2d").drawImage(bitmap, (bitmap.width - side) / 2, (bitmap.height - side) / 2, side, side, 0, 0, SIZE, SIZE);
  bitmap.close();
  return canvas.toDataURL("image/jpeg", 0.85);
}

// "AM" for Alex Mieses; one letter when only one name (or just the email) is known.
const initials = (user) =>
  ([user.first_name, user.last_name].filter(Boolean).map((n) => n.charAt(0)).join("") || user.email.charAt(0)).toUpperCase();

// Avatar markup for anyone (teammates, message senders): photo or initials.
export function avatarMarkup(person, size = "avatar-sm") {
  const inner = person.avatar ? `<img src="${esc(person.avatar)}" alt="">` : esc(initials(person));
  return `<span class="avatar ${size}" aria-hidden="true">${inner}</span>`;
}

// Overlapping avatars that spread apart and reveal each name on hover/focus.
export function avatarGroup(people, max = 6) {
  const shown = people.slice(0, max);
  const extra = people.length - shown.length;
  const items = shown.map((p) => {
    const name = [p.first_name, p.last_name].filter(Boolean).join(" ") || p.email.split("@")[0];
    return `<li class="ag-item" tabindex="0" aria-label="${esc(name)}">${avatarMarkup(p)}<span class="ag-name">${esc(name)}</span></li>`;
  });
  if (extra > 0) items.push(`<li class="ag-item ag-more" aria-label="${extra} more"><span class="avatar avatar-sm">+${extra}</span></li>`);
  return `<ul class="avatar-group" aria-label="Team members">${items.join("")}</ul>`;
}

// Shows the signed-in user's photo (or initials) in every avatar on the page.
export function paintAvatars(user) {
  for (const id of ["avatar", "side-avatar", "settings-avatar"]) {
    const el = document.getElementById(id);
    if (user.avatar) {
      const img = new Image();
      img.src = user.avatar;
      img.alt = "";
      el.replaceChildren(img);
    } else {
      el.textContent = initials(user);
    }
    el.classList.toggle("has-photo", Boolean(user.avatar));
  }
  document.getElementById("photo-remove").hidden = !user.avatar;
}
