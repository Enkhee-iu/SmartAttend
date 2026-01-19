import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...\n');

  // Create sample users
  const admin = await prisma.user.upsert({
    where: { email: 'admin@smartattend.com' },
    update: {},
    create: {
      email: 'admin@smartattend.com',
      name: 'Admin User',
      role: 'ADMIN',
    },
  });

  const teacher = await prisma.user.upsert({
    where: { email: 'teacher@smartattend.com' },
    update: {},
    create: {
      email: 'teacher@smartattend.com',
      name: 'Teacher User',
      role: 'TEACHER',
    },
  });

  const student = await prisma.user.upsert({
    where: { email: 'student@smartattend.com' },
    update: {},
    create: {
      email: 'student@smartattend.com',
      name: 'Student User',
      role: 'STUDENT',
    },
  });

  console.log('✅ Created users:');
  console.log(`   - ${admin.name} (${admin.role})`);
  console.log(`   - ${teacher.name} (${teacher.role})`);
  console.log(`   - ${student.name} (${student.role})`);

  // Create sample attendance records
  const attendance1 = await prisma.attendance.create({
    data: {
      userId: student.id,
      type: 'PRESENT',
      recognizedBy: 'FACE',
      location: 'Main Hall',
      notes: 'On time',
    },
  });

  const attendance2 = await prisma.attendance.create({
    data: {
      userId: student.id,
      type: 'LATE',
      recognizedBy: 'MANUAL',
      location: 'Classroom A',
      notes: 'Arrived 10 minutes late',
    },
  });

  console.log('\n✅ Created attendance records:');
  console.log(`   - ${attendance1.type} at ${attendance1.location}`);
  console.log(`   - ${attendance2.type} at ${attendance2.location}`);

  console.log('\n🎉 Seeding completed successfully!');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
