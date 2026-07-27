import { getMatches, getNews } from "../lib/server-api";
import { HomeClient } from "../components/HomeClient";

/**
 * Bosh sahifa — server komponent.
 *
 * Ilgari butun sahifa "use client" edi: Google va Telegram bo'sh HTML ko'rardi,
 * kontent faqat brauzerda JavaScript ishlagach paydo bo'lardi. Endi ma'lumot
 * serverda yuklanadi va tayyor HTML yuboriladi; interaktivlik va jonli
 * yangilanishlar HomeClient ichida qoladi.
 */
export default async function Home() {
  const [matches, news] = await Promise.all([getMatches(), getNews()]);

  const liveCount = matches.filter((m) => m.status === "LIVE").length;

  return (
    <>
      <HomeClient initialMatches={matches} initialNews={news} />

      {/* Qidiruv tizimlari uchun qisqacha tavsif */}
      <p className="sr-only">
        AI Football Hub Uzbekistan — jonli futbol natijalari, o'yin
        statistikasi va sun'iy intellekt tahlillari. Ayni paytda {liveCount} ta
        o'yin jonli efirda, jami {matches.length} ta uchrashuv kuzatilmoqda.
      </p>
    </>
  );
}
